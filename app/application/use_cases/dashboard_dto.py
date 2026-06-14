# app/application/use_cases/dashboard_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class DashboardResponse:
    period: str
    total_returns: int
    p2p_routes: int
    resell_routes: int
    refurbish_routes: int
    donation_routes: int
    scrap_routes: int
    accepted_buyers: int
    rejected_buyers: int
    tamper_alerts: int
    fraud_overrides: int
    revenue_recovered: Decimal
    average_recovery_rate: float
    average_return_probability: float
    computed_at: datetime
