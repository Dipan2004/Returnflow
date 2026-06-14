# app/infrastructure/persistence/dashboard_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.dashboard_metrics import DashboardMetrics

ENTITY_TYPE_DASHBOARD = "DASHBOARD_METRICS"


def dashboard_pk() -> str:
    return "STATS#GLOBAL"


def dashboard_sk(period: str) -> str:
    return f"PERIOD#{period}"


def to_item(metrics: DashboardMetrics) -> dict[str, Any]:
    return {
        "PK": dashboard_pk(),
        "SK": dashboard_sk(metrics.period),
        "entity_type": ENTITY_TYPE_DASHBOARD,
        "period": metrics.period,
        "total_returns": metrics.total_returns,
        "p2p_routes": metrics.p2p_routes,
        "resell_routes": metrics.resell_routes,
        "refurbish_routes": metrics.refurbish_routes,
        "donation_routes": metrics.donation_routes,
        "scrap_routes": metrics.scrap_routes,
        "accepted_buyers": metrics.accepted_buyers,
        "rejected_buyers": metrics.rejected_buyers,
        "tamper_alerts": metrics.tamper_alerts,
        "fraud_overrides": metrics.fraud_overrides,
        "revenue_recovered": Decimal(str(metrics.revenue_recovered)),
        "average_recovery_rate": Decimal(str(metrics.average_recovery_rate)),
        "average_return_probability": Decimal(str(metrics.average_return_probability)),
        "computed_at": metrics.computed_at.isoformat(),
    }


def from_item(item: dict[str, Any]) -> DashboardMetrics:
    return DashboardMetrics(
        period=item["period"],
        total_returns=int(item["total_returns"]),
        p2p_routes=int(item["p2p_routes"]),
        resell_routes=int(item["resell_routes"]),
        refurbish_routes=int(item.get("refurbish_routes", 0)),
        donation_routes=int(item["donation_routes"]),
        scrap_routes=int(item.get("scrap_routes", 0)),
        accepted_buyers=int(item["accepted_buyers"]),
        rejected_buyers=int(item["rejected_buyers"]),
        tamper_alerts=int(item["tamper_alerts"]),
        fraud_overrides=int(item["fraud_overrides"]),
        revenue_recovered=Decimal(str(item["revenue_recovered"])),
        average_recovery_rate=float(item["average_recovery_rate"]),
        average_return_probability=float(item["average_return_probability"]),
        computed_at=datetime.fromisoformat(item["computed_at"]).replace(tzinfo=UTC),
    )
