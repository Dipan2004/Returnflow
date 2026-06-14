# tests/fakes/fake_buyer_matching_port.py | 22 lines
from __future__ import annotations

from app.application.ports.buyer_matching_port import BuyerMatchingPort


class FakeBuyerMatchingPort(BuyerMatchingPort):
    def __init__(self, default_count: int = 3) -> None:
        self._counts: dict[str, int] = {}
        self._default = default_count

    def set_count(self, sku_id: str, count: int) -> None:
        self._counts[sku_id] = count

    async def get_available_buyer_count(self, sku_id: str, pincode: str) -> int:
        return self._counts.get(sku_id, self._default)