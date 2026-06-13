from __future__ import annotations

from app.application.ports.return_repository import ReturnRepository
from app.domain.entities.return_request import ReturnRequest
from app.domain.value_objects.return_id import ReturnId


class FakeReturnRepository(ReturnRepository):
    def __init__(self) -> None:
        self._store: dict[str, ReturnRequest] = {}

    async def save(self, return_request: ReturnRequest) -> None:
        self._store[return_request.return_id.value] = return_request

    async def get_by_id(self, return_id: ReturnId) -> ReturnRequest | None:
        return self._store.get(return_id.value)

    async def get_by_id_str(self, return_id: str) -> ReturnRequest | None:
        return self._store.get(return_id)

    async def get_by_seller(self, seller_id: str, limit: int = 50) -> list[ReturnRequest]:
        items = [r for r in self._store.values() if r.seller_id == seller_id]
        return sorted(items, key=lambda r: r.created_at, reverse=True)[:limit]

    async def get_by_buyer(self, buyer_id: str, limit: int = 50) -> list[ReturnRequest]:
        items = [r for r in self._store.values() if r.buyer_id == buyer_id]
        return sorted(items, key=lambda r: r.created_at, reverse=True)[:limit]
