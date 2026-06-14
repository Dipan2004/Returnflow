# app/application/use_cases/calculate_disposition_use_case.py
from __future__ import annotations

from decimal import Decimal

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.demand_signal_port import DemandSignalPort
from app.application.ports.disposition_repository import DispositionRepository
from app.application.ports.fraud_history_port import FraudHistoryPort
from app.application.ports.fraud_repository import FraudRepository
from app.application.ports.product_catalog_port import ProductCatalogPort
from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.disposition_dto import (
    DispositionRequest,
    DispositionResponse,
    RecoveryBreakdown,
)
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.services.disposition_engine import DispositionEngine
from app.domain.services.fraud_engine import FraudEngine
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CalculateDispositionUseCase:
    def __init__(
        self,
        return_repository: ReturnRepository,
        condition_grade_repository: ConditionGradeRepository,
        disposition_repository: DispositionRepository,
        demand_signal_port: DemandSignalPort,
        product_catalog_port: ProductCatalogPort,
        disposition_engine: DispositionEngine,
        fraud_history_port: FraudHistoryPort,
        fraud_repository: FraudRepository,
        fraud_engine: FraudEngine,
    ) -> None:
        self._returns = return_repository
        self._grades = condition_grade_repository
        self._dispositions = disposition_repository
        self._demand = demand_signal_port
        self._catalog = product_catalog_port
        self._engine = disposition_engine
        self._fraud_history = fraud_history_port
        self._fraud_repository = fraud_repository
        self._fraud_engine = fraud_engine

    async def execute(self, request: DispositionRequest) -> DispositionResponse:
        return_id = ReturnId(request.return_id)

        return_request = await self._returns.get_by_id(return_id)
        if return_request is None:
            raise EntityNotFoundError("ReturnRequest", request.return_id)

        condition_grade = await self._grades.get_by_return_id(return_id)
        if condition_grade is None:
            raise EntityNotFoundError("ConditionGrade", request.return_id)

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

        buyer_info = await self._demand.get_nearest_buyer(
            sku_id=request.sku_id,
            seller_pincode=request.seller_pincode,
        )
        has_demand = buyer_info is not None
        matched_buyer_id: str | None = None
        distance_km: float | None = None
        if buyer_info is not None:
            matched_buyer_id, distance_km = buyer_info

        decision = self._engine.calculate(
            return_id=return_id,
            grade=condition_grade.grade,
            mrp=mrp,
            has_p2p_demand=has_demand,
            distance_km=distance_km,
            matched_buyer_id=matched_buyer_id,
        )

        fraud_history = await self._fraud_history.get_buyer_history(
            buyer_id=return_request.buyer_id,
            sku_id=request.sku_id,
            window_hours=self._fraud_engine._window_hours,
        )

        fraud_assessment = self._fraud_engine.assess(
            return_id=return_id,
            buyer_id=return_request.buyer_id,
            sku_id=request.sku_id,
            total_returns_in_window=fraud_history.total_returns_in_window,
            high_value_returns_in_window=fraud_history.high_value_returns_in_window,
            same_sku_returns_in_window=fraud_history.same_sku_returns_in_window,
            returns_last_24h=fraud_history.returns_last_24h,
            original_route=decision.route,
        )

        await self._fraud_repository.save(fraud_assessment)

        if fraud_assessment.requires_route_override:
            decision = self._engine.calculate_with_fraud_override(
                return_id=return_id,
                grade=condition_grade.grade,
                mrp=mrp,
            )
            logger.warning(
                "Fraud override applied",
                return_id=request.return_id,
                original_route=fraud_assessment.override_reason.original_route
                if fraud_assessment.override_reason
                else "UNKNOWN",
                risk_score=fraud_assessment.risk_score,
            )

        await self._dispositions.save(decision)

        logger.info(
            "Disposition calculated",
            return_id=request.return_id,
            grade=condition_grade.grade.value,
            route=decision.route.value,
            fraud_level=fraud_assessment.risk_level.value,
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
            fraud_flagged=fraud_assessment.requires_route_override,
            matched_buyer_id=decision.matched_buyer_id,
            distance_km=decision.distance_km,
            decided_at=decision.decided_at,
        )
