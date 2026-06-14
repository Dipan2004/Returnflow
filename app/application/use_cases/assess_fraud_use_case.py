# app/application/use_cases/assess_fraud_use_case.py
from __future__ import annotations

from app.application.ports.fraud_history_port import FraudHistoryPort
from app.application.ports.fraud_repository import FraudRepository
from app.application.use_cases.fraud_dto import (
    FraudAssessmentRequest,
    FraudAssessmentResponse,
    FraudOverrideDTO,
    FraudSignalDTO,
)
from app.domain.services.fraud_engine import FraudEngine
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class AssessFraudUseCase:
    def __init__(
        self,
        fraud_history_port: FraudHistoryPort,
        fraud_repository: FraudRepository,
        fraud_engine: FraudEngine,
    ) -> None:
        self._history = fraud_history_port
        self._repository = fraud_repository
        self._engine = fraud_engine

    async def execute(self, request: FraudAssessmentRequest) -> FraudAssessmentResponse:
        return_id = ReturnId(request.return_id)

        history = await self._history.get_buyer_history(
            buyer_id=request.buyer_id,
            sku_id=request.sku_id,
            window_hours=self._engine._window_hours,
        )

        original_route: Route | None = None
        if request.original_route:
            original_route = Route.from_string(request.original_route)

        assessment = self._engine.assess(
            return_id=return_id,
            buyer_id=request.buyer_id,
            sku_id=request.sku_id,
            total_returns_in_window=history.total_returns_in_window,
            high_value_returns_in_window=history.high_value_returns_in_window,
            same_sku_returns_in_window=history.same_sku_returns_in_window,
            returns_last_24h=history.returns_last_24h,
            original_route=original_route,
        )

        await self._repository.save(assessment)

        logger.info(
            "Fraud assessment completed",
            return_id=request.return_id,
            risk_level=assessment.risk_level.value,
            risk_score=assessment.risk_score,
            override=assessment.override_reason is not None,
        )

        override_dto: FraudOverrideDTO | None = None
        if assessment.override_reason:
            override_dto = FraudOverrideDTO(
                original_route=assessment.override_reason.original_route,
                overridden_route=assessment.override_reason.overridden_route,
                risk_level=assessment.override_reason.risk_level,
                risk_score=assessment.override_reason.risk_score,
                reason=assessment.override_reason.reason,
            )

        return FraudAssessmentResponse(
            return_id=request.return_id,
            buyer_id=assessment.buyer_id,
            sku_id=assessment.sku_id,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level.value,
            signals=[
                FraudSignalDTO(
                    name=s.name,
                    weight=s.weight,
                    triggered=s.triggered,
                    detail=s.detail,
                )
                for s in assessment.signals
            ],
            override=override_dto,
            assessed_at=assessment.assessed_at,
        )
