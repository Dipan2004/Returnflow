# app/api/schemas/dashboard_schemas.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardMetricsResponse(BaseModel):
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
