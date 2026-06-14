# app/api/schemas/orchestration_schemas.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrchestrationResponseSchema(BaseModel):
    return_id: str
    route: str
    recovery_value: Decimal
    decision_reason: str
    fraud_override_applied: bool
    buyer_match_used: bool
    demand_score: int
    confidence: float
    grade: str
    liquidation_baseline: Decimal
    value_delta: Decimal
    recovery_percentage: float
    decided_at: datetime
