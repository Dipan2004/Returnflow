# app/application/ports/buyer_matching_port.py | 18 lines
from __future__ import annotations

from abc import ABC, abstractmethod


class BuyerMatchingPort(ABC):
    @abstractmethod
    async def get_available_buyer_count(self, sku_id: str, pincode: str) -> int: ...