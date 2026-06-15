# app/infrastructure/persistence/in_memory_health_card_repository.py
from __future__ import annotations

from app.application.ports.health_card_repository import HealthCardRepository
from app.domain.entities.health_card import HealthCard
from app.domain.entities.qr_token import QRToken
from app.domain.exceptions import QRTokenNotFoundError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryHealthCardRepository(HealthCardRepository):
    def __init__(self) -> None:
        STORE.setdefault("health_cards", {})
        STORE.setdefault("qr_tokens", {})

    async def save(self, health_card: HealthCard) -> None:
        STORE["health_cards"][health_card.return_id.value] = health_card

    async def get_by_return_id(self, return_id: ReturnId) -> HealthCard | None:
        return STORE["health_cards"].get(return_id.value)

    async def save_qr_token(self, qr_token: QRToken) -> None:
        STORE["qr_tokens"][qr_token.token] = qr_token

    async def get_qr_token(self, token: str) -> QRToken | None:
        return STORE["qr_tokens"].get(token)

    async def consume_qr_token(self, token: str, agent_id: str) -> QRToken:
        qr = STORE["qr_tokens"].get(token)
        if qr is None:
            raise QRTokenNotFoundError(token)
        qr.consume(agent_id)
        STORE["qr_tokens"][token] = qr
        return qr
