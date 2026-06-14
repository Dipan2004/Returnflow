# app/domain/services/dashboard_aggregation_engine.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.dashboard_metrics import DashboardMetrics


class DashboardAggregationEngine:
    def compute(
        self,
        period: str,
        route_counts: dict[str, int],
        accepted: int,
        rejected: int,
        tamper_alerts: int,
        fraud_overrides: int,
        total_recovery: Decimal,
        total_returns: int,
        avg_return_probability: float,
    ) -> DashboardMetrics:
        avg_recovery = (
            float(total_recovery / Decimal(str(total_returns)) * 100)
            if total_returns > 0
            else 0.0
        )
        return DashboardMetrics(
            period=period,
            total_returns=total_returns,
            p2p_routes=route_counts.get("P2P", 0),
            resell_routes=route_counts.get("RESELL", 0),
            refurbish_routes=route_counts.get("REFURBISH", 0),
            donation_routes=route_counts.get("DONATE", 0),
            scrap_routes=route_counts.get("SCRAP", 0),
            accepted_buyers=accepted,
            rejected_buyers=rejected,
            tamper_alerts=tamper_alerts,
            fraud_overrides=fraud_overrides,
            revenue_recovered=total_recovery,
            average_recovery_rate=round(avg_recovery, 2),
            average_return_probability=round(avg_return_probability, 4),
            computed_at=datetime.now(UTC),
        )
