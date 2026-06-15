# app/infrastructure/persistence/in_memory_buyer_match_repository.py
from __future__ import annotations

from app.application.ports.buyer_match_repository import BuyerMatchRepository
from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryBuyerMatchRepository(BuyerMatchRepository):
    def __init__(self) -> None:
        STORE.setdefault("buyer_matches", {})

    async def save(self, result: BuyerMatchResult) -> None:
        STORE["buyer_matches"][result.return_id.value] = result

    async def get_by_return_id(self, return_id: ReturnId) -> BuyerMatchResult | None:
        return STORE["buyer_matches"].get(return_id.value)
