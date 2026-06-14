# app/application/use_cases/get_fraud_assessment_use_case.py
from __future__ import annotations

from app.application.ports.fraud_repository import FraudRepository
from app.application.use_cases.fraud_dto import (
    FraudAssessmentResponse,
    FraudOverrideDTO,
    FraudSignalDTO,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetFraudAssessmentUseCase:
    def __init__(self, fraud_repository: FraudRepository) -> None:
        self._repository = fraud_repository

    async def execute(self, return_id_str: str) -> FraudAssessmentResponse:
        return_id = ReturnId(return_id_str)
        assessment = await self._repository.get_by_return_id(return_id)
        if assessment is None:
            raise EntityNotFoundError("FraudAssessment", return_id_str)

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
            return_id=return_id_str,
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
