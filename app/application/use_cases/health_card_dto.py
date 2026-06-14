# app/application/use_cases/health_card_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class HealthCardResponse:
    return_id: str
    sku_id: str
    grade: str
    confidence: float
    damage_description: str
    route: str
    mrp: Decimal
    recovery_value: Decimal
    value_delta: Decimal
    qr_token: str
    verification_url: str
    status: str
    image_keys: list[str]
    created_at: datetime
    fraud_risk: str
    buyer_match_used: bool


@dataclass(frozen=True)
class GenerateHealthCardResult:
    return_id: str
    qr_token: str
    verification_url: str
    route: str
    condition_grade: str
    recovery_value: Decimal
    created_at: datetime
