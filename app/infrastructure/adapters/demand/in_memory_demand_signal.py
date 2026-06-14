# app/infrastructure/adapters/demand/in_memory_demand_signal.py
from __future__ import annotations

from app.application.ports.demand_signal_port import DemandSignalPort

_DEMO_DEMAND: dict[str, tuple[str, float]] = {
    "B08N5WRWNW": ("demo_buyer_99", 2.3),
}


class InMemoryDemandSignal(DemandSignalPort):
    def __init__(self) -> None:
        self._demand: dict[str, tuple[str, float]] = dict(_DEMO_DEMAND)

    async def has_demand(self, sku_id: str, seller_pincode: str) -> bool:
        return sku_id in self._demand

    async def get_nearest_buyer(
        self, sku_id: str, seller_pincode: str
    ) -> tuple[str, float] | None:
        return self._demand.get(sku_id)
