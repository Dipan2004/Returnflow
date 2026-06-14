# app/api/schemas/disposition_schemas.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RecoveryBreakdownResponse(BaseModel):
    mrp: Decimal
    recovery_value: Decimal
    liquidation_baseline: Decimal
    value_delta: Decimal
    recovery_percentage: float


class CalculateDispositionRequest(BaseModel):
    return_id: str = Field(min_length=1)
    sku_id: str = Field(min_length=1)
    seller_pincode: str = Field(min_length=1)
    mrp: Decimal | None = Field(default=None, gt=Decimal("0"))


class DispositionResponse(BaseModel):
    return_id: str
    route: str
    route_label: str
    grade: str
    route_reason: str
    recovery: RecoveryBreakdownResponse
    fraud_flagged: bool
    matched_buyer_id: str | None = None
    distance_km: float | None = None
    decided_at: datetime