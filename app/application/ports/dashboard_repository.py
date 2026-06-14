# app/application/ports/dashboard_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.dashboard_metrics import DashboardMetrics


class DashboardRepository(ABC):
    @abstractmethod
    async def save(self, metrics: DashboardMetrics) -> None: ...

    @abstractmethod
    async def get_latest(self, period: str) -> DashboardMetrics | None: ...
