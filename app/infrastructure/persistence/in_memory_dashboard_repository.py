# app/infrastructure/persistence/in_memory_dashboard_repository.py
from __future__ import annotations

from app.application.ports.dashboard_repository import DashboardRepository
from app.domain.entities.dashboard_metrics import DashboardMetrics
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryDashboardRepository(DashboardRepository):
    def __init__(self) -> None:
        STORE.setdefault("dashboard", {})

    async def save(self, metrics: DashboardMetrics) -> None:
        STORE["dashboard"][metrics.period] = metrics

    async def get_latest(self, period: str) -> DashboardMetrics | None:
        return STORE["dashboard"].get(period)
