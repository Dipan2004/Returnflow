# app/application/use_cases/orchestration_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class OrchestrationResponse:
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
