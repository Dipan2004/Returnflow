# tests/fakes/fake_health_card_repository.py
from __future__ import annotations

from app.application.ports.health_card_repository import HealthCardRepository
from app.domain.entities.health_card import HealthCard
from app.domain.entities.qr_token import QRToken
from app.domain.exceptions import QRTokenNotFoundError
from app.domain.value_objects.return_id import ReturnId


class FakeHealthCardRepository(HealthCardRepository):
    def __init__(self) -> None:
        self._cards: dict[str, HealthCard] = {}
        self._tokens: dict[str, QRToken] = {}

    async def save(self, health_card: HealthCard) -> None:
        self._cards[health_card.return_id.value] = health_card

    async def get_by_return_id(self, return_id: ReturnId) -> HealthCard | None:
        return self._cards.get(return_id.value)

    async def save_qr_token(self, qr_token: QRToken) -> None:
        self._tokens[qr_token.token] = qr_token

    async def get_qr_token(self, token: str) -> QRToken | None:
        return self._tokens.get(token)

    async def consume_qr_token(self, token: str, agent_id: str) -> QRToken:
        qr = self._tokens.get(token)
        if qr is None:
            raise QRTokenNotFoundError(token)
        qr.consume(agent_id)
        self._tokens[token] = qr
        return qr
