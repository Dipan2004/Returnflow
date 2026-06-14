# app/application/ports/demand_index_port.py | 18 lines
from __future__ import annotations

from abc import ABC, abstractmethod


class DemandIndexPort(ABC):
    @abstractmethod
    async def get_demand_score(self, sku_id: str) -> int: ...