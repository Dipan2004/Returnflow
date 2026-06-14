# tests/unit/domain/test_prevent_iq_engine.py
from __future__ import annotations

import pytest

from app.domain.services.prevent_iq_engine import BuyerFeatures, PreventIQEngine, SkuFeatures


def _buyer(return_rate: float = 0.15) -> BuyerFeatures:
    return BuyerFeatures(
        buyer_id="B1",
        return_rate=return_rate,
        total_returns=3,
        avg_days_between_returns=30.0,
        category_preference="apparel",
    )


def _sku(
    mismatch_rate: float = 0.10,
    category_return_rate: float = 0.20,
    keep_rate: float = 0.85,
) -> SkuFeatures:
    return SkuFeatures(
        sku_id="SKU001",
        size="M",
        category_return_rate=category_return_rate,
        size_mismatch_rate=mismatch_rate,
        brand="BrandA",
        recommended_size="M",
        keep_rate_for_recommended=keep_rate,
    )


class TestPreventIQEnginePredict:
    def setup_method(self) -> None:
        self.engine = PreventIQEngine()

    def test_low_risk_prediction(self) -> None:
        result = self.engine.predict(_buyer(0.05), _sku(0.05, 0.10), 0.10)
        assert result.risk_level == "LOW"
        assert result.return_probability.value == 0.10

    def test_medium_risk_prediction(self) -> None:
        result = self.engine.predict(_buyer(0.30), _sku(0.20, 0.30), 0.35)
        assert result.risk_level == "MEDIUM"

    def test_high_risk_prediction(self) -> None:
        result = self.engine.predict(_buyer(0.60), _sku(0.50, 0.50), 0.70)
        assert result.risk_level == "HIGH"

    def test_model_score_capped_at_1(self) -> None:
        result = self.engine.predict(_buyer(), _sku(), 1.5)
        assert result.return_probability.value == 1.0

    def test_size_warning_when_mismatch_high(self) -> None:
        result = self.engine.predict(_buyer(), _sku(mismatch_rate=0.30), 0.30)
        assert result.size_warning is not None
        assert "30%" in result.size_warning

    def test_no_size_warning_when_mismatch_low(self) -> None:
        result = self.engine.predict(_buyer(), _sku(mismatch_rate=0.20), 0.20)
        assert result.size_warning is None

    def test_size_warning_threshold_boundary(self) -> None:
        result = self.engine.predict(_buyer(), _sku(mismatch_rate=0.25), 0.25)
        assert result.size_warning is None

    def test_size_warning_just_above_threshold(self) -> None:
        result = self.engine.predict(_buyer(), _sku(mismatch_rate=0.26), 0.26)
        assert result.size_warning is not None

    def test_keep_rate_from_sku_features(self) -> None:
        result = self.engine.predict(_buyer(), _sku(keep_rate=0.92), 0.30)
        assert result.keep_rate.value == 0.92

    def test_recommended_size_from_sku_features(self) -> None:
        result = self.engine.predict(_buyer(), _sku(), 0.30)
        assert result.recommended_size == "M"

    def test_buyer_id_on_prediction(self) -> None:
        result = self.engine.predict(_buyer(), _sku(), 0.30)
        assert result.buyer_id == "B1"

    def test_sku_id_on_prediction(self) -> None:
        result = self.engine.predict(_buyer(), _sku(), 0.30)
        assert result.sku_id == "SKU001"


class TestPreventIQEngineRecommendSize:
    def setup_method(self) -> None:
        self.engine = PreventIQEngine()

    def test_basic_recommendation(self) -> None:
        sku = _sku(mismatch_rate=0.20)
        result = self.engine.recommend_size("SKU001", "BrandA", "L", sku)
        assert result.recommended_size == "M"
        assert result.current_size == "L"
        assert result.brand == "BrandA"

    def test_confidence_is_inverse_of_mismatch(self) -> None:
        sku = _sku(mismatch_rate=0.30)
        result = self.engine.recommend_size("SKU001", "BrandA", "L", sku)
        assert result.confidence == pytest.approx(0.70)

    def test_mismatch_rate_stored(self) -> None:
        sku = _sku(mismatch_rate=0.45)
        result = self.engine.recommend_size("SKU001", "BrandA", "XL", sku)
        assert result.mismatch_rate == 0.45

    def test_zero_mismatch_full_confidence(self) -> None:
        sku = _sku(mismatch_rate=0.0)
        result = self.engine.recommend_size("SKU001", "BrandA", "M", sku)
        assert result.confidence == 1.0

    def test_sku_id_propagated(self) -> None:
        sku = _sku()
        result = self.engine.recommend_size("SKU999", "BrandX", "S", sku)
        assert result.sku_id == "SKU999"
