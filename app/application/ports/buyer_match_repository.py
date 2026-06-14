# app/application/ports/buyer_match_repository.py | 22 lines
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.value_objects.return_id import ReturnId


class BuyerMatchRepository(ABC):
    @abstractmethod
    async def save(self, result: BuyerMatchResult) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> BuyerMatchResult | None: ...