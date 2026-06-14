# app/infrastructure/adapters/buyer_match/in_memory_buyer_matching_adapter.py | 28 lines
from __future__ import annotations

from app.application.ports.buyer_matching_port import BuyerMatchingPort

_DEFAULT_BUYER_COUNT = 3

_DEMO_BUYERS: dict[str, int] = {
    "SKU001": 8,
    "SKU002": 4,
    "SKU003": 0,
}


class InMemoryBuyerMatchingAdapter(BuyerMatchingPort):
    def __init__(self) -> None:
        self._buyers: dict[str, int] = dict(_DEMO_BUYERS)

    async def get_available_buyer_count(self, sku_id: str, pincode: str) -> int:
        return self._buyers.get(sku_id, _DEFAULT_BUYER_COUNT)