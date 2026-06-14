# tests/unit/infrastructure/test_fraud_mapper.py
from __future__ import annotations

from app.domain.entities.fraud_assessment import (
    FraudAssessment,
    FraudOverrideReason,
    FraudRiskLevel,
    FraudSignal,
)
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.fraud_mapper import from_item, to_item


def _make_signals() -> list[FraudSignal]:
    return [
        FraudSignal(name="S1", weight=30, triggered=True, detail="hit"),
        FraudSignal(name="S2", weight=25, triggered=False, detail="ok"),
    ]


def test_to_item_contains_required_keys() -> None:
    a = FraudAssessment.create(
        return_id=ReturnId("TEST1"), buyer_id="buyer_1", sku_id="SKU_1",
        signals=_make_signals(),
    )
    item = to_item(a)
    assert item["PK"] == "RETURN#TEST1"
    assert item["SK"] == "FRAUD_ASSESSMENT"
    assert item["entity_type"] == "FRAUD_ASSESSMENT"
    assert item["risk_score"] == 30
    assert item["risk_level"] == "LOW"


def test_roundtrip_without_override() -> None:
    original = FraudAssessment.create(
        return_id=ReturnId("TEST2"), buyer_id="buyer_1", sku_id="SKU_1",
        signals=_make_signals(),
    )
    item = to_item(original)
    restored = from_item(item)
    assert restored.return_id == original.return_id
    assert restored.risk_score == original.risk_score
    assert restored.risk_level == original.risk_level
    assert len(restored.signals) == 2
    assert restored.override_reason is None


def test_roundtrip_with_override() -> None:
    override = FraudOverrideReason(
        original_route="P2P", overridden_route="RESELL",
        risk_level="HIGH", risk_score=80, reason="fraud override"
    )
    original = FraudAssessment.create(
        return_id=ReturnId("TEST3"), buyer_id="buyer_1", sku_id="SKU_1",
        signals=_make_signals(), override_reason=override,
    )
    item = to_item(original)
    restored = from_item(item)
    assert restored.override_reason is not None
    assert restored.override_reason.original_route == "P2P"
    assert restored.override_reason.overridden_route == "RESELL"


def test_signal_serialization() -> None:
    signals = [FraudSignal(name="X", weight=50, triggered=True, detail="test")]
    a = FraudAssessment.create(
        return_id=ReturnId("TEST4"), buyer_id="b", sku_id="s", signals=signals
    )
    item = to_item(a)
    assert item["signals"][0]["name"] == "X"
    assert item["signals"][0]["weight"] == 50
    assert item["signals"][0]["triggered"] is True


def test_from_item_parses_risk_level() -> None:
    signals = [
        FraudSignal(name="S1", weight=30, triggered=True, detail="hit"),
        FraudSignal(name="S2", weight=25, triggered=True, detail="hit"),
        FraudSignal(name="S3", weight=25, triggered=True, detail="hit"),
    ]
    a = FraudAssessment.create(
        return_id=ReturnId("TEST5"), buyer_id="b", sku_id="s", signals=signals
    )
    item = to_item(a)
    restored = from_item(item)
    assert restored.risk_level == FraudRiskLevel.HIGH
