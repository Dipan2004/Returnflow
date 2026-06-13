from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.health_card import HealthCard
from app.domain.entities.qr_token import QRToken
from app.domain.value_objects.return_id import ReturnId


class HealthCardRepository(ABC):
    @abstractmethod
    async def save(self, health_card: HealthCard) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> HealthCard | None: ...

    @abstractmethod
    async def save_qr_token(self, qr_token: QRToken) -> None: ...

    @abstractmethod
    async def get_qr_token(self, token: str) -> QRToken | None: ...

    @abstractmethod
    async def consume_qr_token(self, token: str, agent_id: str) -> QRToken: ...