# app/application/use_cases/get_health_card_use_case.py
from __future__ import annotations

from app.application.ports.health_card_repository import HealthCardRepository
from app.application.use_cases.health_card_dto import HealthCardResponse
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetHealthCardUseCase:
    def __init__(self, health_card_repository: HealthCardRepository) -> None:
        self._repository = health_card_repository

    async def execute(self, return_id_str: str) -> HealthCardResponse:
        return_id = ReturnId(return_id_str)
        health_card = await self._repository.get_by_return_id(return_id)
        if health_card is None:
            raise EntityNotFoundError("HealthCard", return_id_str)

        return HealthCardResponse(
            return_id=return_id_str,
            sku_id=health_card.sku_id,
            grade=health_card.grade.value,
            confidence=health_card.confidence.value,
            damage_description=health_card.damage_description,
            route=health_card.route.value,
            mrp=health_card.mrp.amount,
            recovery_value=health_card.recovery_value.amount,
            value_delta=health_card.value_delta.amount,
            qr_token=health_card.qr_token,
            verification_url=health_card.qr_url,
            status=health_card.status.value,
            image_keys=[k.value for k in health_card.image_keys],
            created_at=health_card.created_at,
            fraud_risk="UNKNOWN",
            buyer_match_used=False,
        )
