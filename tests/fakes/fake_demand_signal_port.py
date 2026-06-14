# tests/fakes/fake_demand_signal_port.py
from __future__ import annotations

from app.application.ports.demand_signal_port import DemandSignalPort


class FakeDemandSignalPort(DemandSignalPort):
    """In-memory demand signal fake for tests."""

    def __init__(
        self,
        *,
        buyer_id: str = "buyer_nearby",
        distance_km: float = 2.5,
        has_demand: bool = True,
    ) -> None:
        self._has_demand = has_demand
        self._buyer_id = buyer_id
        self._distance_km = distance_km
        # Per-SKU overrides: sku_id -> (buyer_id, distance_km) | None
        self._overrides: dict[str, tuple[str, float] | None] = {}

    # --- test helpers ---

    def set_demand(self, sku_id: str, buyer_id: str, distance_km: float) -> None:
        self._overrides[sku_id] = (buyer_id, distance_km)

    def set_no_demand(self, sku_id: str) -> None:
        self._overrides[sku_id] = None

    def set_global_demand(self, *, has_demand: bool) -> None:
        self._has_demand = has_demand

    # --- port implementation ---

    async def has_demand(self, sku_id: str, seller_pincode: str) -> bool:
        if sku_id in self._overrides:
            return self._overrides[sku_id] is not None
        return self._has_demand

    async def get_nearest_buyer(
        self, sku_id: str, seller_pincode: str
    ) -> tuple[str, float] | None:
        if sku_id in self._overrides:
            return self._overrides[sku_id]
        if not self._has_demand:
            return None
        return (self._buyer_id, self._distance_km)