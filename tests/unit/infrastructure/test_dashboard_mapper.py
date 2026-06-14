# tests/unit/infrastructure/test_dashboard_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.dashboard_metrics import DashboardMetrics
from app.infrastructure.persistence.dashboard_mapper import from_item, to_item


def _make_metrics() -> DashboardMetrics:
    return DashboardMetrics(
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


def test_roundtrip() -> None:
    original = _make_metrics()
    item = to_item(original)
    restored = from_item(item)
    assert restored.period == original.period
    assert restored.total_returns == original.total_returns
    assert restored.p2p_routes == 30


def test_pk_sk() -> None:
    m = _make_metrics()
    item = to_item(m)
    assert item["PK"] == "STATS#GLOBAL"
    assert item["SK"] == "PERIOD#last_30_days"


def test_entity_type() -> None:
    item = to_item(_make_metrics())
    assert item["entity_type"] == "DASHBOARD_METRICS"
