# app/infrastructure/adapters/buyer_match/in_memory_demand_index.py | 28 lines
from __future__ import annotations

from app.application.ports.demand_index_port import DemandIndexPort

_DEFAULT_DEMAND_SCORE = 50

_DEMO_DEMAND: dict[str, int] = {
    "SKU001": 85,
    "SKU002": 72,
    "SKU003": 25,
}


class InMemoryDemandIndex(DemandIndexPort):
    def __init__(self) -> None:
        self._index: dict[str, int] = dict(_DEMO_DEMAND)

    async def get_demand_score(self, sku_id: str) -> int:
        return self._index.get(sku_id, _DEFAULT_DEMAND_SCORE)