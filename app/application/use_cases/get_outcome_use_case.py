# app/application/use_cases/get_outcome_use_case.py
from __future__ import annotations

from app.application.ports.outcome_repository import OutcomeRepository
from app.application.use_cases.outcome_dto import OutcomeResponse
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetOutcomeUseCase:
    def __init__(self, outcome_repository: OutcomeRepository) -> None:
        self._outcomes = outcome_repository

    async def execute(self, return_id_str: str) -> OutcomeResponse:
        return_id = ReturnId(return_id_str)
        outcome = await self._outcomes.get_by_return_id(return_id)
        if outcome is None:
            raise EntityNotFoundError("DispositionOutcome", return_id_str)
        return OutcomeResponse(
            return_id=return_id_str,
            buyer_id=outcome.buyer_id,
            route=outcome.route,
            status=outcome.status.value,
            recovery_value=outcome.recovery_value,
            fraud_flag=outcome.fraud_flag,
            outcome_reason=outcome.outcome_reason,
            created_at=outcome.created_at,
            resolved_at=outcome.resolved_at,
        )
