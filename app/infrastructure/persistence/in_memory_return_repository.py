# app/infrastructure/persistence/in_memory_return_repository.py
from __future__ import annotations

from app.application.ports.return_repository import ReturnRepository
from app.domain.entities.return_request import ReturnRequest
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryReturnRepository(ReturnRepository):
    def __init__(self) -> None:
        STORE.setdefault("returns", {})

    async def save(self, return_request: ReturnRequest) -> None:
        STORE["returns"][return_request.return_id.value] = return_request

    async def get_by_id(self, return_id: ReturnId) -> ReturnRequest | None:
        return STORE["returns"].get(return_id.value)

    async def get_by_seller(self, seller_id: str, limit: int = 50) -> list[ReturnRequest]:
        items = [r for r in STORE["returns"].values() if isinstance(r, ReturnRequest) and r.seller_id == seller_id]
        return sorted(items, key=lambda r: r.created_at, reverse=True)[:limit]

    async def get_by_buyer(self, buyer_id: str, limit: int = 50) -> list[ReturnRequest]:
        items = [r for r in STORE["returns"].values() if isinstance(r, ReturnRequest) and r.buyer_id == buyer_id]
        return sorted(items, key=lambda r: r.created_at, reverse=True)[:limit]
