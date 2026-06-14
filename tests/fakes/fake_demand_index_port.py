# tests/fakes/fake_demand_index_port.py | 22 lines
from __future__ import annotations

from app.application.ports.demand_index_port import DemandIndexPort


class FakeDemandIndexPort(DemandIndexPort):
    def __init__(self, default_score: int = 50) -> None:
        self._scores: dict[str, int] = {}
        self._default = default_score

    def set_score(self, sku_id: str, score: int) -> None:
        self._scores[sku_id] = score

    async def get_demand_score(self, sku_id: str) -> int:
        return self._scores.get(sku_id, self._default)