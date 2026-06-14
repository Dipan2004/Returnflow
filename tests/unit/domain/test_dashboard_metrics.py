# tests/unit/domain/test_dashboard_metrics.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.dashboard_metrics import DashboardMetrics


def test_dashboard_metrics_creation() -> None:
    m = DashboardMetrics(
        period="last_30_days",
        total_returns=100,
        p2p_routes=30,
        resell_routes=40,
        refurbish_routes=15,
        donation_routes=10,
        scrap_routes=5,
        accepted_buyers=25,
        rejected_buyers=5,
        tamper_alerts=2,
        fraud_overrides=3,
        revenue_recovered=Decimal("480000.00"),
        average_recovery_rate=65.5,
        average_return_probability=0.15,
        computed_at=datetime.now(UTC),
    )
    assert m.total_returns == 100
    assert m.p2p_routes == 30


def test_dashboard_metrics_zero_state() -> None:
    m = DashboardMetrics(
        period="empty",
        total_returns=0,
        p2p_routes=0,
        resell_routes=0,
        refurbish_routes=0,
        donation_routes=0,
        scrap_routes=0,
        accepted_buyers=0,
        rejected_buyers=0,
        tamper_alerts=0,
        fraud_overrides=0,
        revenue_recovered=Decimal("0"),
        average_recovery_rate=0.0,
        average_return_probability=0.0,
        computed_at=datetime.now(UTC),
    )
    assert m.revenue_recovered == Decimal("0")
