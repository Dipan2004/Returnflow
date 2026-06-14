# app/infrastructure/persistence/fraud_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.fraud_assessment import (
    FraudAssessment,
    FraudOverrideReason,
    FraudRiskLevel,
    FraudSignal,
)
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_FRAUD = "FRAUD_ASSESSMENT"


def fraud_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def fraud_sk() -> str:
    return "FRAUD_ASSESSMENT"


def to_item(assessment: FraudAssessment) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": fraud_pk(assessment.return_id),
        "SK": fraud_sk(),
        "entity_type": ENTITY_TYPE_FRAUD,
        "return_id": assessment.return_id.value,
        "buyer_id": assessment.buyer_id,
        "sku_id": assessment.sku_id,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level.value,
        "signals": [
            {
                "name": s.name,
                "weight": s.weight,
                "triggered": s.triggered,
                "detail": s.detail,
            }
            for s in assessment.signals
        ],
        "assessed_at": assessment.assessed_at.isoformat(),
    }
    if assessment.override_reason:
        item["override_reason"] = {
            "original_route": assessment.override_reason.original_route,
            "overridden_route": assessment.override_reason.overridden_route,
            "risk_level": assessment.override_reason.risk_level,
            "risk_score": assessment.override_reason.risk_score,
            "reason": assessment.override_reason.reason,
        }
    return item


def from_item(item: dict[str, Any]) -> FraudAssessment:
    signals = [
        FraudSignal(
            name=s["name"],
            weight=int(s["weight"]),
            triggered=bool(s["triggered"]),
            detail=s["detail"],
        )
        for s in item.get("signals", [])
    ]

    override: FraudOverrideReason | None = None
    raw_override = item.get("override_reason")
    if raw_override:
        override = FraudOverrideReason(
            original_route=raw_override["original_route"],
            overridden_route=raw_override["overridden_route"],
            risk_level=raw_override["risk_level"],
            risk_score=int(raw_override["risk_score"]),
            reason=raw_override["reason"],
        )

    return FraudAssessment(
        return_id=ReturnId(item["return_id"]),
        buyer_id=item["buyer_id"],
        sku_id=item["sku_id"],
        risk_score=int(item["risk_score"]),
        risk_level=FraudRiskLevel(item["risk_level"]),
        signals=signals,
        override_reason=override,
        assessed_at=datetime.fromisoformat(item["assessed_at"]).replace(tzinfo=UTC),
    )
