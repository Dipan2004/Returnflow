# tests/fakes/fake_dashboard_repository.py
from __future__ import annotations

from app.application.ports.dashboard_repository import DashboardRepository
from app.domain.entities.dashboard_metrics import DashboardMetrics


class FakeDashboardRepository(DashboardRepository):
    def __init__(self) -> None:
        self._store: dict[str, DashboardMetrics] = {}

    async def save(self, metrics: DashboardMetrics) -> None:
        self._store[metrics.period] = metrics

    async def get_latest(self, period: str) -> DashboardMetrics | None:
        return self._store.get(period)
