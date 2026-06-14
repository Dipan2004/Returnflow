# app/api/schemas/outcome_schemas.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OutcomeResponseSchema(BaseModel):
    return_id: str
    buyer_id: str
    route: str
    status: str
    recovery_value: Decimal
    fraud_flag: bool
    outcome_reason: str
    created_at: datetime
    resolved_at: datetime | None = None


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)
