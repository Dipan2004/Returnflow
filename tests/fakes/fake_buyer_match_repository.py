# tests/fakes/fake_buyer_match_repository.py | 26 lines
from __future__ import annotations

from app.application.ports.buyer_match_repository import BuyerMatchRepository
from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.value_objects.return_id import ReturnId


class FakeBuyerMatchRepository(BuyerMatchRepository):
    def __init__(self) -> None:
        self._store: dict[str, BuyerMatchResult] = {}

    async def save(self, result: BuyerMatchResult) -> None:
        self._store[result.return_id.value] = result

    async def get_by_return_id(self, return_id: ReturnId) -> BuyerMatchResult | None:
        return self._store.get(return_id.value)

    def count(self) -> int:
        return len(self._store)