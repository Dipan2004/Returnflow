# tests/unit/application/test_get_dashboard_metrics_use_case.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.use_cases.get_dashboard_metrics_use_case import GetDashboardMetricsUseCase
from app.domain.entities.dashboard_metrics import DashboardMetrics
from app.domain.services.dashboard_aggregation_engine import DashboardAggregationEngine
from tests.fakes.fake_dashboard_repository import FakeDashboardRepository


@pytest.mark.asyncio
async def test_returns_stored_metrics() -> None:
    repo = FakeDashboardRepository()
    m = DashboardMetrics(
        period="last_30_days",
        total_returns=50,
        p2p_routes=20,
        resell_routes=20,
        refurbish_routes=5,
        donation_routes=3,
        scrap_routes=2,
        accepted_buyers=18,
        rejected_buyers=2,
        tamper_alerts=1,
        fraud_overrides=2,
        revenue_recovered=Decimal("250000"),
        average_recovery_rate=65.0,
        average_return_probability=0.12,
        computed_at=datetime.now(UTC),
    )
    await repo.save(m)
    uc = GetDashboardMetricsUseCase(
        dashboard_repository=repo, aggregation_engine=DashboardAggregationEngine()
    )
    result = await uc.execute("last_30_days")
    assert result.total_returns == 50


@pytest.mark.asyncio
async def test_returns_empty_when_no_data() -> None:
    repo = FakeDashboardRepository()
    uc = GetDashboardMetricsUseCase(
        dashboard_repository=repo, aggregation_engine=DashboardAggregationEngine()
    )
    result = await uc.execute("last_7_days")
    assert result.total_returns == 0


@pytest.mark.asyncio
async def test_default_period() -> None:
    repo = FakeDashboardRepository()
    uc = GetDashboardMetricsUseCase(
        dashboard_repository=repo, aggregation_engine=DashboardAggregationEngine()
    )
    result = await uc.execute()
    assert result.period == "last_30_days"
