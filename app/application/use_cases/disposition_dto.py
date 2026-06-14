# app/application/use_cases/disposition_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class DispositionRequest:
    return_id: str
    sku_id: str
    seller_pincode: str
    mrp: Decimal | None = None


@dataclass(frozen=True)
class RecoveryBreakdown:
    mrp: Decimal
    recovery_value: Decimal
    liquidation_baseline: Decimal
    value_delta: Decimal
    recovery_percentage: float


@dataclass(frozen=True)
class DispositionResponse:
    return_id: str
    route: str
    route_label: str
    grade: str
    route_reason: str
    recovery: RecoveryBreakdown
    fraud_flagged: bool
    matched_buyer_id: str | None
    distance_km: float | None
    decided_at: datetime
