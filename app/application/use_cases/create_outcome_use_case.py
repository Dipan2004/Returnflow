# app/application/use_cases/create_outcome_use_case.py
from __future__ import annotations

from decimal import Decimal

from app.application.ports.outcome_repository import OutcomeRepository
from app.application.use_cases.outcome_dto import OutcomeResponse
from app.domain.entities.disposition_outcome import DispositionOutcome
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CreateOutcomeUseCase:
    def __init__(self, outcome_repository: OutcomeRepository) -> None:
        self._outcomes = outcome_repository

    async def execute(
        self,
        return_id_str: str,
        buyer_id: str,
        route: str,
        recovery_value: Decimal,
        fraud_flag: bool = False,
    ) -> OutcomeResponse:
        return_id = ReturnId(return_id_str)
        outcome = DispositionOutcome.create_pending(
            return_id=return_id,
            buyer_id=buyer_id,
            route=route,
            recovery_value=recovery_value,
            fraud_flag=fraud_flag,
        )
        await self._outcomes.save(outcome)
        logger.info("Outcome created", return_id=return_id_str, route=route)
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
