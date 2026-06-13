from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.api.schemas.common import BaseSchema
from app.domain.entities.health_card import HealthCardStatus
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.route import Route


class DamageLabelResponse(BaseSchema):
    name: str
    confidence: float


class HealthCardResponse(BaseSchema):
    return_id: str
    sku_id: str
    grade: Grade
    confidence: float
    damage_description: str
    damage_labels: list[DamageLabelResponse]
    route: Route
    mrp: Decimal
    recovery_value: Decimal
    value_delta: Decimal
    image_urls: list[str]
    qr_url: str
    status: HealthCardStatus
    created_at: datetime
    accepted_at: datetime | None = None
    disputed_at: datetime | None = None
    dispute_reason: str | None = None


class QRVerifyResponse(BaseSchema):
    valid: bool
    return_id: str | None = None
    reason: str | None = None
    alert: str | None = None
    scanned_at: datetime | None = None


class DisputeRequest(BaseSchema):
    reason: str = Field(min_length=10, max_length=500)


class AcceptResponse(BaseSchema):
    return_id: str
    status: HealthCardStatus
    accepted_at: datetime


class FlywheelStatsResponse(BaseSchema):
    period: str
    returns_processed: int
    value_recovered_inr: Decimal
    waste_diverted_kg: float
    p2p_match_count: int
    p2p_match_accuracy_current: float
    p2p_match_accuracy_baseline: float
    co2_avoided_kg: float