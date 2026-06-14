# tests/unit/domain/test_fraud_assessment.py
from __future__ import annotations

import pytest

from app.domain.entities.fraud_assessment import (
    FraudAssessment,
    FraudOverrideReason,
    FraudRiskLevel,
    FraudSignal,
)
from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


class TestFraudRiskLevel:
    def test_low_from_score_zero(self) -> None:
        assert FraudRiskLevel.from_score(0) == FraudRiskLevel.LOW

    def test_low_from_score_39(self) -> None:
        assert FraudRiskLevel.from_score(39) == FraudRiskLevel.LOW

    def test_medium_from_score_40(self) -> None:
        assert FraudRiskLevel.from_score(40) == FraudRiskLevel.MEDIUM

    def test_medium_from_score_69(self) -> None:
        assert FraudRiskLevel.from_score(69) == FraudRiskLevel.MEDIUM

    def test_high_from_score_70(self) -> None:
        assert FraudRiskLevel.from_score(70) == FraudRiskLevel.HIGH

    def test_high_from_score_100(self) -> None:
        assert FraudRiskLevel.from_score(100) == FraudRiskLevel.HIGH

    def test_invalid_score_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudRiskLevel.from_score(101)

    def test_negative_score_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudRiskLevel.from_score(-1)


class TestFraudSignal:
    def test_valid_signal(self) -> None:
        s = FraudSignal(name="TEST", weight=30, triggered=True, detail="test detail")
        assert s.name == "TEST"
        assert s.weight == 30

    def test_empty_name_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudSignal(name="", weight=30, triggered=True, detail="x")

    def test_invalid_weight_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudSignal(name="X", weight=101, triggered=True, detail="x")

    def test_negative_weight_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudSignal(name="X", weight=-1, triggered=True, detail="x")


class TestFraudAssessment:
    def test_create_low_risk(self) -> None:
        signals = [
            FraudSignal(name="S1", weight=20, triggered=False, detail="ok"),
            FraudSignal(name="S2", weight=30, triggered=False, detail="ok"),
        ]
        a = FraudAssessment.create(
            return_id=ReturnId.generate(),
            buyer_id="buyer_1",
            sku_id="SKU_1",
            signals=signals,
        )
        assert a.risk_score == 0
        assert a.risk_level == FraudRiskLevel.LOW
        assert not a.requires_route_override

    def test_create_medium_risk(self) -> None:
        signals = [
            FraudSignal(name="S1", weight=25, triggered=True, detail="hit"),
            FraudSignal(name="S2", weight=25, triggered=True, detail="hit"),
        ]
        a = FraudAssessment.create(
            return_id=ReturnId.generate(),
            buyer_id="buyer_1",
            sku_id="SKU_1",
            signals=signals,
        )
        assert a.risk_score == 50
        assert a.risk_level == FraudRiskLevel.MEDIUM
        assert not a.requires_route_override

    def test_create_high_risk(self) -> None:
        signals = [
            FraudSignal(name="S1", weight=30, triggered=True, detail="hit"),
            FraudSignal(name="S2", weight=25, triggered=True, detail="hit"),
            FraudSignal(name="S3", weight=25, triggered=True, detail="hit"),
        ]
        a = FraudAssessment.create(
            return_id=ReturnId.generate(),
            buyer_id="buyer_1",
            sku_id="SKU_1",
            signals=signals,
        )
        assert a.risk_score == 80
        assert a.risk_level == FraudRiskLevel.HIGH
        assert a.requires_route_override

    def test_score_capped_at_100(self) -> None:
        signals = [
            FraudSignal(name="S1", weight=60, triggered=True, detail="hit"),
            FraudSignal(name="S2", weight=60, triggered=True, detail="hit"),
        ]
        a = FraudAssessment.create(
            return_id=ReturnId.generate(),
            buyer_id="buyer_1",
            sku_id="SKU_1",
            signals=signals,
        )
        assert a.risk_score == 100

    def test_triggered_signals_only_counts_triggered(self) -> None:
        signals = [
            FraudSignal(name="S1", weight=30, triggered=True, detail="hit"),
            FraudSignal(name="S2", weight=30, triggered=False, detail="ok"),
        ]
        a = FraudAssessment.create(
            return_id=ReturnId.generate(),
            buyer_id="buyer_1",
            sku_id="SKU_1",
            signals=signals,
        )
        assert len(a.triggered_signals) == 1
        assert a.risk_score == 30

    def test_empty_buyer_id_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudAssessment.create(
                return_id=ReturnId.generate(),
                buyer_id="",
                sku_id="SKU",
                signals=[],
            )

    def test_empty_sku_id_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            FraudAssessment.create(
                return_id=ReturnId.generate(),
                buyer_id="buyer",
                sku_id="",
                signals=[],
            )

    def test_override_reason_stored(self) -> None:
        override = FraudOverrideReason(
            original_route="P2P",
            overridden_route="RESELL",
            risk_level="HIGH",
            risk_score=80,
            reason="Test override",
        )
        a = FraudAssessment.create(
            return_id=ReturnId.generate(),
            buyer_id="buyer_1",
            sku_id="SKU_1",
            signals=[],
            override_reason=override,
        )
        assert a.override_reason is not None
        assert a.override_reason.overridden_route == "RESELL"
