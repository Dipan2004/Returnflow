# tests/unit/domain/test_dashboard_aggregation_engine.py
from __future__ import annotations

from decimal import Decimal

from app.domain.services.dashboard_aggregation_engine import DashboardAggregationEngine


class TestDashboardAggregationEngine:
    def setup_method(self) -> None:
        self.engine = DashboardAggregationEngine()

    def test_compute_with_data(self) -> None:
        m = self.engine.compute(
            period="last_30_days",
            route_counts={"P2P": 30, "RESELL": 40, "REFURBISH": 15, "DONATE": 10, "SCRAP": 5},
            accepted=25,
            rejected=5,
            tamper_alerts=2,
            fraud_overrides=3,
            total_recovery=Decimal("480000"),
            total_returns=100,
            avg_return_probability=0.15,
        )
        assert m.total_returns == 100
        assert m.p2p_routes == 30
        assert m.resell_routes == 40
        assert m.fraud_overrides == 3
        assert m.average_return_probability == 0.15

    def test_compute_empty_returns(self) -> None:
        m = self.engine.compute(
            period="empty",
            route_counts={},
            accepted=0,
            rejected=0,
            tamper_alerts=0,
            fraud_overrides=0,
            total_recovery=Decimal("0"),
            total_returns=0,
            avg_return_probability=0.0,
        )
        assert m.average_recovery_rate == 0.0
        assert m.total_returns == 0

    def test_recovery_rate_calculation(self) -> None:
        m = self.engine.compute(
            period="test",
            route_counts={"P2P": 10},
            accepted=8,
            rejected=2,
            tamper_alerts=0,
            fraud_overrides=0,
            total_recovery=Decimal("65000"),
            total_returns=10,
            avg_return_probability=0.2,
        )
        assert m.average_recovery_rate > 0

    def test_missing_route_defaults_zero(self) -> None:
        m = self.engine.compute(
            period="test",
            route_counts={"P2P": 5},
            accepted=5,
            rejected=0,
            tamper_alerts=0,
            fraud_overrides=0,
            total_recovery=Decimal("10000"),
            total_returns=5,
            avg_return_probability=0.1,
        )
        assert m.scrap_routes == 0
        assert m.donation_routes == 0
