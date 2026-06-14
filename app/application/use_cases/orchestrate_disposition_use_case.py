# app/application/use_cases/orchestrate_disposition_use_case.py
from __future__ import annotations

from app.application.ports.buyer_match_repository import BuyerMatchRepository
from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.disposition_repository import DispositionRepository
from app.application.ports.fraud_repository import FraudRepository
from app.application.ports.product_catalog_port import ProductCatalogPort
from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.orchestration_dto import (
    OrchestrationResponse,
)
from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.services.disposition_orchestrator import DispositionOrchestrator
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class OrchestrateDispositionUseCase:
    def __init__(
        self,
        return_repository: ReturnRepository,
        condition_grade_repository: ConditionGradeRepository,
        fraud_repository: FraudRepository,
        buyer_match_repository: BuyerMatchRepository,
        disposition_repository: DispositionRepository,
        product_catalog_port: ProductCatalogPort,
        orchestrator: DispositionOrchestrator,
    ) -> None:
        self._returns = return_repository
        self._grades = condition_grade_repository
        self._fraud = fraud_repository
        self._buyer_match = buyer_match_repository
        self._dispositions = disposition_repository
        self._catalog = product_catalog_port
        self._orchestrator = orchestrator

    async def execute(self, return_id_str: str) -> OrchestrationResponse:
        return_id = ReturnId(return_id_str)

        return_request = await self._returns.get_by_id(return_id)
        if return_request is None:
            raise EntityNotFoundError("ReturnRequest", return_id_str)

        condition_grade = await self._grades.get_by_return_id(return_id)
        if condition_grade is None:
            raise EntityNotFoundError("ConditionGrade", return_id_str)

        fraud_assessment = await self._fraud.get_by_return_id(return_id)
        if fraud_assessment is None:
            raise EntityNotFoundError("FraudAssessment", return_id_str)

        buyer_match = await self._buyer_match.get_by_return_id(return_id)

        mrp_decimal = await self._catalog.get_mrp(return_request.sku_id)
        if mrp_decimal is None:
            raise DomainValidationError(
                f"MRP not found for SKU '{return_request.sku_id}'"
            )
        mrp = Money.of(mrp_decimal)

        decision = self._orchestrator.decide(
            return_id=return_id,
            condition_grade=condition_grade,
            fraud_assessment=fraud_assessment,
            buyer_match=buyer_match,
            mrp=mrp,
        )

        matched_buyer_id: str | None = None
        distance_km: float | None = None
        if decision.route == Route.P2P and buyer_match is not None:
            matched_buyer_id = "p2p_matched_buyer"
            distance_km = 2.0

        disposition_entity = DispositionDecision(
            return_id=return_id,
            route=decision.route,
            grade=decision.grade,
            mrp=decision.mrp,
            recovery_value=decision.recovery_value,
            liquidation_baseline=decision.liquidation_baseline,
            route_reason=decision.decision_reason,
            fraud_flagged=decision.fraud_override_applied,
            decided_at=decision.decided_at,
            matched_buyer_id=matched_buyer_id,
            distance_km=distance_km,
        )

        await self._dispositions.save(disposition_entity)

        logger.info(
            "Disposition orchestrated",
            return_id=return_id_str,
            route=decision.route.value,
            fraud_override=decision.fraud_override_applied,
            buyer_match_used=decision.buyer_match_used,
        )

        return OrchestrationResponse(
            return_id=return_id_str,
            route=decision.route.value,
            recovery_value=decision.recovery_value.amount,
            decision_reason=decision.decision_reason,
            fraud_override_applied=decision.fraud_override_applied,
            buyer_match_used=decision.buyer_match_used,
            demand_score=decision.demand_score,
            confidence=decision.confidence,
            grade=decision.grade.value,
            liquidation_baseline=decision.liquidation_baseline.amount,
            value_delta=decision.value_delta.amount,
            recovery_percentage=decision.recovery_percentage,
            decided_at=decision.decided_at,
        )
