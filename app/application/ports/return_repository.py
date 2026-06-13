from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.return_request import ReturnRequest
from app.domain.value_objects.return_id import ReturnId


class ReturnRepository(ABC):
    @abstractmethod
    async def save(self, return_request: ReturnRequest) -> None: ...

    @abstractmethod
    async def get_by_id(self, return_id: ReturnId) -> ReturnRequest | None: ...

    @abstractmethod
    async def get_by_seller(self, seller_id: str, limit: int = 50) -> list[ReturnRequest]: ...

    @abstractmethod
    async def get_by_buyer(self, buyer_id: str, limit: int = 50) -> list[ReturnRequest]: ...