# app/infrastructure/persistence/disposition_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route

ENTITY_TYPE_DISPOSITION = "DISPOSITION_DECISION"


def disposition_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def disposition_sk() -> str:
    return "DISPOSITION"


def to_item(decision: DispositionDecision) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": disposition_pk(decision.return_id),
        "SK": disposition_sk(),
        "entity_type": ENTITY_TYPE_DISPOSITION,
        "return_id": decision.return_id.value,
        "route": decision.route.value,
        "grade": decision.grade.value,
        "mrp_amount": Decimal(str(decision.mrp.amount)),
        "mrp_currency": decision.mrp.currency,
        "recovery_value_amount": Decimal(str(decision.recovery_value.amount)),
        "liquidation_baseline_amount": Decimal(str(decision.liquidation_baseline.amount)),
        "value_delta_amount": Decimal(str(decision.value_delta.amount)),
        "route_reason": decision.route_reason,
        "fraud_flagged": decision.fraud_flagged,
        "decided_at": decision.decided_at.isoformat(),
    }
    if decision.matched_buyer_id is not None:
        item["matched_buyer_id"] = decision.matched_buyer_id
    if decision.distance_km is not None:
        item["distance_km"] = Decimal(str(decision.distance_km))
    return item


def from_item(item: dict[str, Any]) -> DispositionDecision:
    currency = item.get("mrp_currency", "INR")
    mrp = Money.of(item["mrp_amount"], currency)
    recovery_value = Money.of(item["recovery_value_amount"], currency)
    liquidation_baseline = Money.of(item["liquidation_baseline_amount"], currency)

    distance_km: float | None = None
    raw_dist = item.get("distance_km")
    if raw_dist is not None:
        distance_km = float(raw_dist)

    matched_buyer_id: str | None = item.get("matched_buyer_id")

    return DispositionDecision(
        return_id=ReturnId(item["return_id"]),
        route=Route.from_string(item["route"]),
        grade=Grade.from_string(item["grade"]),
        mrp=mrp,
        recovery_value=recovery_value,
        liquidation_baseline=liquidation_baseline,
        route_reason=item["route_reason"],
        fraud_flagged=bool(item.get("fraud_flagged", False)),
        decided_at=datetime.fromisoformat(item["decided_at"]).replace(tzinfo=UTC),
        matched_buyer_id=matched_buyer_id,
        distance_km=distance_km,
    )