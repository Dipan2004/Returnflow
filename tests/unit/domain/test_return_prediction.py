# tests/unit/domain/test_return_prediction.py
from __future__ import annotations

import pytest

from app.domain.entities.return_prediction import ReturnPrediction
from app.domain.entities.size_recommendation import SizeRecommendation
from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.keep_rate import KeepRate
from app.domain.value_objects.return_probability import ReturnProbability
from app.domain.value_objects.size_risk import SizeRisk


class TestReturnProbability:
    def test_valid_zero(self) -> None:
        rp = ReturnProbability(0.0)
        assert rp.value == 0.0

    def test_valid_one(self) -> None:
        rp = ReturnProbability(1.0)
        assert rp.value == 1.0

    def test_valid_mid(self) -> None:
        rp = ReturnProbability(0.5)
        assert rp.value == 0.5

    def test_below_zero_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            ReturnProbability(-0.01)

    def test_above_one_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            ReturnProbability(1.01)

    def test_risk_level_low(self) -> None:
        assert ReturnProbability(0.0).risk_level == "LOW"
        assert ReturnProbability(0.19).risk_level == "LOW"

    def test_risk_level_medium(self) -> None:
        assert ReturnProbability(0.2).risk_level == "MEDIUM"
        assert ReturnProbability(0.49).risk_level == "MEDIUM"

    def test_risk_level_high(self) -> None:
        assert ReturnProbability(0.5).risk_level == "HIGH"
        assert ReturnProbability(1.0).risk_level == "HIGH"

    def test_equality(self) -> None:
        assert ReturnProbability(0.5) == ReturnProbability(0.5)
        assert ReturnProbability(0.3) != ReturnProbability(0.7)

    def test_repr(self) -> None:
        assert "0.5" in repr(ReturnProbability(0.5))


class TestKeepRate:
    def test_valid(self) -> None:
        kr = KeepRate(0.85)
        assert kr.value == 0.85

    def test_zero(self) -> None:
        kr = KeepRate(0.0)
        assert kr.value == 0.0

    def test_one(self) -> None:
        kr = KeepRate(1.0)
        assert kr.value == 1.0

    def test_below_zero_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            KeepRate(-0.1)

    def test_above_one_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            KeepRate(1.1)

    def test_equality(self) -> None:
        assert KeepRate(0.5) == KeepRate(0.5)
        assert KeepRate(0.5) != KeepRate(0.6)

    def test_repr(self) -> None:
        assert "0.85" in repr(KeepRate(0.85))


class TestSizeRisk:
    def test_low_from_rate(self) -> None:
        assert SizeRisk.from_mismatch_rate(0.0) == SizeRisk.LOW
        assert SizeRisk.from_mismatch_rate(0.24) == SizeRisk.LOW

    def test_medium_from_rate(self) -> None:
        assert SizeRisk.from_mismatch_rate(0.25) == SizeRisk.MEDIUM
        assert SizeRisk.from_mismatch_rate(0.49) == SizeRisk.MEDIUM

    def test_high_from_rate(self) -> None:
        assert SizeRisk.from_mismatch_rate(0.5) == SizeRisk.HIGH
        assert SizeRisk.from_mismatch_rate(0.9) == SizeRisk.HIGH


class TestReturnPredictionEntity:
    def test_create(self) -> None:
        pred = ReturnPrediction.create(
            buyer_id="B1",
            sku_id="S1",
            size="M",
            return_probability=ReturnProbability(0.3),
            keep_rate=KeepRate(0.85),
            size_warning=None,
            recommended_size="M",
        )
        assert pred.buyer_id == "B1"
        assert pred.sku_id == "S1"
        assert pred.risk_level == "MEDIUM"
        assert pred.predicted_at is not None

    def test_empty_buyer_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            ReturnPrediction.create(
                buyer_id="",
                sku_id="S1",
                size="M",
                return_probability=ReturnProbability(0.3),
                keep_rate=KeepRate(0.85),
                size_warning=None,
                recommended_size="M",
            )

    def test_empty_sku_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            ReturnPrediction.create(
                buyer_id="B1",
                sku_id="",
                size="M",
                return_probability=ReturnProbability(0.3),
                keep_rate=KeepRate(0.85),
                size_warning=None,
                recommended_size="M",
            )

    def test_empty_size_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            ReturnPrediction.create(
                buyer_id="B1",
                sku_id="S1",
                size="",
                return_probability=ReturnProbability(0.3),
                keep_rate=KeepRate(0.85),
                size_warning=None,
                recommended_size="M",
            )

    def test_repr(self) -> None:
        pred = ReturnPrediction.create(
            buyer_id="B1",
            sku_id="S1",
            size="M",
            return_probability=ReturnProbability(0.3),
            keep_rate=KeepRate(0.85),
            size_warning=None,
            recommended_size="M",
        )
        assert "ReturnPrediction" in repr(pred)


class TestSizeRecommendationEntity:
    def test_create(self) -> None:
        rec = SizeRecommendation(
            sku_id="S1",
            current_size="L",
            recommended_size="M",
            confidence=0.8,
            mismatch_rate=0.2,
            brand="TestBrand",
        )
        assert rec.sku_id == "S1"
        assert rec.recommended_size == "M"

    def test_empty_sku_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            SizeRecommendation(
                sku_id="",
                current_size="L",
                recommended_size="M",
                confidence=0.8,
                mismatch_rate=0.2,
                brand="TestBrand",
            )

    def test_invalid_confidence_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            SizeRecommendation(
                sku_id="S1",
                current_size="L",
                recommended_size="M",
                confidence=1.5,
                mismatch_rate=0.2,
                brand="TestBrand",
            )

    def test_invalid_mismatch_rate_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            SizeRecommendation(
                sku_id="S1",
                current_size="L",
                recommended_size="M",
                confidence=0.8,
                mismatch_rate=-0.1,
                brand="TestBrand",
            )

    def test_empty_brand_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            SizeRecommendation(
                sku_id="S1",
                current_size="L",
                recommended_size="M",
                confidence=0.8,
                mismatch_rate=0.2,
                brand="",
            )

    def test_repr(self) -> None:
        rec = SizeRecommendation(
            sku_id="S1",
            current_size="L",
            recommended_size="M",
            confidence=0.8,
            mismatch_rate=0.2,
            brand="TestBrand",
        )
        assert "SizeRecommendation" in repr(rec)
