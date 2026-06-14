# app/application/use_cases/get_health_card_by_qr_use_case.py
from __future__ import annotations

from app.application.ports.health_card_repository import HealthCardRepository
from app.application.use_cases.health_card_dto import HealthCardResponse
from app.domain.exceptions import EntityNotFoundError, QRTokenNotFoundError


class GetHealthCardByQRUseCase:
    def __init__(self, health_card_repository: HealthCardRepository) -> None:
        self._repository = health_card_repository

    async def execute(self, qr_token: str) -> HealthCardResponse:
        token_entity = await self._repository.get_qr_token(qr_token)
        if token_entity is None:
            raise QRTokenNotFoundError(qr_token)

        health_card = await self._repository.get_by_return_id(token_entity.return_id)
        if health_card is None:
            raise EntityNotFoundError("HealthCard", token_entity.return_id.value)

        return HealthCardResponse(
            return_id=health_card.return_id.value,
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
