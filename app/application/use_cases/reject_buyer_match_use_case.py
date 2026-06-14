# app/application/use_cases/reject_buyer_match_use_case.py
from __future__ import annotations

from app.application.ports.health_card_repository import HealthCardRepository
from app.application.ports.outcome_repository import OutcomeRepository
from app.application.use_cases.outcome_dto import OutcomeResponse
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class RejectBuyerMatchUseCase:
    def __init__(
        self,
        outcome_repository: OutcomeRepository,
        health_card_repository: HealthCardRepository,
    ) -> None:
        self._outcomes = outcome_repository
        self._health_cards = health_card_repository

    async def execute(
        self, buyer_id: str, return_id_str: str, reason: str
    ) -> OutcomeResponse:
        return_id = ReturnId(return_id_str)
        outcome = await self._outcomes.get_by_return_id(return_id)
        if outcome is None:
            raise EntityNotFoundError("DispositionOutcome", return_id_str)
        if outcome.buyer_id != buyer_id:
            raise DomainValidationError("Buyer ID does not match the outcome")

        outcome.reject(reason)
        await self._outcomes.save(outcome)

        health_card = await self._health_cards.get_by_return_id(return_id)
        if health_card is not None:
            health_card.dispute(reason)
            await self._health_cards.save(health_card)

        logger.info("Buyer rejected", return_id=return_id_str, buyer_id=buyer_id)

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
