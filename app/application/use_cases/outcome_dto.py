# app/application/use_cases/outcome_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class OutcomeResponse:
    return_id: str
    buyer_id: str
    route: str
    status: str
    recovery_value: Decimal
    fraud_flag: bool
    outcome_reason: str
    created_at: datetime
    resolved_at: datetime | None
