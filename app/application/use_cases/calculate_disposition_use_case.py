# app/application/use_cases/calculate_disposition_use_case.py
from __future__ import annotations

from decimal import Decimal

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.demand_signal_port import DemandSignalPort
from app.application.ports.disposition_repository import DispositionRepository
from app.application.ports.product_catalog_port import ProductCatalogPort
from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.disposition_dto import (
    DispositionRequest,
    DispositionResponse,
    RecoveryBreakdown,
)
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.services.disposition_engine import DispositionEngine
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CalculateDispositionUseCase:
    """
    Orchestrates the full disposition calculation:

    1. Load ReturnRequest (to get sku_id, seller_pincode, buyer_id).
    2. Load ConditionGrade (for the grade).
    3. Resolve MRP: from request override or ProductCatalogPort.
    4. Query DemandSignalPort for P2P buyer availability.
    5. Invoke DispositionEngine.calculate().
    6. Persist the DispositionDecision.
    7. Return DispositionResponse DTO.
    """

    def __init__(
        self,
        return_repository: ReturnRepository,
        condition_grade_repository: ConditionGradeRepository,
        disposition_repository: DispositionRepository,
        demand_signal_port: DemandSignalPort,
        product_catalog_port: ProductCatalogPort,
        disposition_engine: DispositionEngine,
    ) -> None:
        self._returns = return_repository
        self._grades = condition_grade_repository
        self._dispositions = disposition_repository
        self._demand = demand_signal_port
        self._catalog = product_catalog_port
        self._engine = disposition_engine

    async def execute(self, request: DispositionRequest) -> DispositionResponse:
        return_id = ReturnId(request.return_id)

        return_request = await self._returns.get_by_id(return_id)
        if return_request is None:
            raise EntityNotFoundError("ReturnRequest", request.return_id)

        condition_grade = await self._grades.get_by_return_id(return_id)
        if condition_grade is None:
            raise EntityNotFoundError("ConditionGrade", request.return_id)

        # Resolve MRP
        mrp_decimal: Decimal
        if request.mrp is not None:
            mrp_decimal = request.mrp
        else:
            catalog_mrp = await self._catalog.get_mrp(request.sku_id)
            if catalog_mrp is None:
                raise DomainValidationError(
                    f"MRP not found in catalog for SKU '{request.sku_id}'. "
                    "Provide an explicit mrp in the request."
                )
            mrp_decimal = catalog_mrp

        mrp = Money.of(mrp_decimal)

        # Query demand
        buyer_info = await self._demand.get_nearest_buyer(
            sku_id=request.sku_id,
            seller_pincode=request.seller_pincode,
        )
        has_demand = buyer_info is not None
        matched_buyer_id: str | None = None
        distance_km: float | None = None
        if buyer_info is not None:
            matched_buyer_id, distance_km = buyer_info

        # Run engine
        decision = self._engine.calculate(
            return_id=return_id,
            grade=condition_grade.grade,
            mrp=mrp,
            has_p2p_demand=has_demand,
            distance_km=distance_km,
            matched_buyer_id=matched_buyer_id,
        )

        await self._dispositions.save(decision)

        logger.info(
            "Disposition calculated",
            return_id=request.return_id,
            grade=condition_grade.grade.value,
            route=decision.route.value,
            recovery_value=str(decision.recovery_value),
            value_delta=str(decision.value_delta),
        )

        recovery_pct = float(
            decision.recovery_value.amount / mrp_decimal * 100
        ) if mrp_decimal else 0.0

        return DispositionResponse(
            return_id=request.return_id,
            route=decision.route.value,
            route_label=decision.route.display_label,
            grade=decision.grade.value,
            route_reason=decision.route_reason,
            recovery=RecoveryBreakdown(
                mrp=decision.mrp.amount,
                recovery_value=decision.recovery_value.amount,
                liquidation_baseline=decision.liquidation_baseline.amount,
                value_delta=decision.value_delta.amount,
                recovery_percentage=recovery_pct,
            ),
            fraud_flagged=decision.fraud_flagged,
            matched_buyer_id=decision.matched_buyer_id,
            distance_km=decision.distance_km,
            decided_at=decision.decided_at,
        )