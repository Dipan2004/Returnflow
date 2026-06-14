# app/infrastructure/persistence/health_card_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.health_card import HealthCard, HealthCardStatus
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route

ENTITY_TYPE_HEALTH_CARD = "HEALTH_CARD"


def health_card_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def health_card_sk() -> str:
    return "HEALTH_CARD"


def to_item(health_card: HealthCard) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": health_card_pk(health_card.return_id),
        "SK": health_card_sk(),
        "entity_type": ENTITY_TYPE_HEALTH_CARD,
        "return_id": health_card.return_id.value,
        "sku_id": health_card.sku_id,
        "grade": health_card.grade.value,
        "confidence": Decimal(str(health_card.confidence.value)),
        "damage_description": health_card.damage_description,
        "route": health_card.route.value,
        "mrp_amount": Decimal(str(health_card.mrp.amount)),
        "recovery_value_amount": Decimal(str(health_card.recovery_value.amount)),
        "value_delta_amount": Decimal(str(health_card.value_delta.amount)),
        "image_keys": [k.value for k in health_card.image_keys],
        "qr_token": health_card.qr_token,
        "qr_url": health_card.qr_url,
        "status": health_card.status.value,
        "created_at": health_card.created_at.isoformat(),
        "ttl_hours": health_card.ttl_hours,
    }
    if health_card.accepted_at:
        item["accepted_at"] = health_card.accepted_at.isoformat()
    if health_card.disputed_at:
        item["disputed_at"] = health_card.disputed_at.isoformat()
    if health_card.dispute_reason:
        item["dispute_reason"] = health_card.dispute_reason
    return item


def from_item(item: dict[str, Any]) -> HealthCard:
    return HealthCard(
        return_id=ReturnId(item["return_id"]),
        sku_id=item["sku_id"],
        grade=Grade.from_string(item["grade"]),
        confidence=ConfidenceScore.of(float(item["confidence"])),
        damage_description=item["damage_description"],
        route=Route.from_string(item["route"]),
        mrp=Money.of(item["mrp_amount"]),
        recovery_value=Money.of(item["recovery_value_amount"]),
        value_delta=Money.of(item["value_delta_amount"]),
        image_keys=[ImageKey(k) for k in item.get("image_keys", [])],
        qr_token=item["qr_token"],
        qr_url=item["qr_url"],
        created_at=datetime.fromisoformat(item["created_at"]).replace(tzinfo=UTC),
        ttl_hours=int(item["ttl_hours"]),
        status=HealthCardStatus(item["status"]),
        dispute_reason=item.get("dispute_reason"),
        accepted_at=_parse_dt(item.get("accepted_at")),
        disputed_at=_parse_dt(item.get("disputed_at")),
    )


def _parse_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=UTC)
