# app/infrastructure/persistence/outcome_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.disposition_outcome import DispositionOutcome, OutcomeStatus
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_OUTCOME = "DISPOSITION_OUTCOME"


def outcome_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def outcome_sk() -> str:
    return "OUTCOME"


def to_item(outcome: DispositionOutcome) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": outcome_pk(outcome.return_id),
        "SK": outcome_sk(),
        "entity_type": ENTITY_TYPE_OUTCOME,
        "return_id": outcome.return_id.value,
        "buyer_id": outcome.buyer_id,
        "route": outcome.route,
        "status": outcome.status.value,
        "recovery_value": Decimal(str(outcome.recovery_value)),
        "fraud_flag": outcome.fraud_flag,
        "outcome_reason": outcome.outcome_reason,
        "created_at": outcome.created_at.isoformat(),
    }
    if outcome.resolved_at:
        item["resolved_at"] = outcome.resolved_at.isoformat()
    return item


def from_item(item: dict[str, Any]) -> DispositionOutcome:
    resolved_at = None
    if item.get("resolved_at"):
        resolved_at = datetime.fromisoformat(item["resolved_at"]).replace(tzinfo=UTC)
    return DispositionOutcome(
        return_id=ReturnId(item["return_id"]),
        buyer_id=item["buyer_id"],
        route=item["route"],
        status=OutcomeStatus(item["status"]),
        recovery_value=Decimal(str(item["recovery_value"])),
        fraud_flag=bool(item.get("fraud_flag", False)),
        outcome_reason=item["outcome_reason"],
        created_at=datetime.fromisoformat(item["created_at"]).replace(tzinfo=UTC),
        resolved_at=resolved_at,
    )
