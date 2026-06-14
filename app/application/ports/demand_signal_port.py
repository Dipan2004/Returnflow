# app/application/ports/demand_signal_port.py
from __future__ import annotations

from abc import ABC, abstractmethod


class DemandSignalPort(ABC):
    """Port for querying real-time P2P buyer demand signals."""

    @abstractmethod
    async def has_demand(self, sku_id: str, seller_pincode: str) -> bool:
        """Return True if at least one active buyer exists within radius."""
        ...

    @abstractmethod
    async def get_nearest_buyer(
        self, sku_id: str, seller_pincode: str
    ) -> tuple[str, float] | None:
        """Return (buyer_id, distance_km) for nearest buyer, or None."""
        ...