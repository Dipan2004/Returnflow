# tests/unit/application/test_get_size_recommendation_use_case.py
from __future__ import annotations

import pytest

from app.application.ports.sku_feature_port import SkuFeatures
from app.application.use_cases.get_size_recommendation_use_case import (
    GetSizeRecommendationUseCase,
)
from app.domain.services.prevent_iq_engine import PreventIQEngine
from tests.fakes.fake_sku_feature_port import FakeSkuFeaturePort


@pytest.fixture
def sku_port() -> FakeSkuFeaturePort:
    port = FakeSkuFeaturePort()
    port.set_features(
        "SKU1",
        "L",
        SkuFeatures(
            category_return_rate=0.20,
            size_mismatch_rate=0.35,
            brand="BrandX",
            recommended_size="M",
            keep_rate_for_recommended=0.90,
        ),
    )
    return port


@pytest.fixture
def use_case(sku_port: FakeSkuFeaturePort) -> GetSizeRecommendationUseCase:
    return GetSizeRecommendationUseCase(
        sku_feature_port=sku_port,
        prevent_iq_engine=PreventIQEngine(),
    )


class TestGetSizeRecommendationUseCase:
    @pytest.mark.asyncio
    async def test_returns_recommended_size(
        self, use_case: GetSizeRecommendationUseCase
    ) -> None:
        response = await use_case.execute("SKU1", "L")
        assert response.recommended_size == "M"

    @pytest.mark.asyncio
    async def test_current_size(self, use_case: GetSizeRecommendationUseCase) -> None:
        response = await use_case.execute("SKU1", "L")
        assert response.current_size == "L"

    @pytest.mark.asyncio
    async def test_confidence(self, use_case: GetSizeRecommendationUseCase) -> None:
        response = await use_case.execute("SKU1", "L")
        assert response.confidence == pytest.approx(0.65)

    @pytest.mark.asyncio
    async def test_mismatch_rate(self, use_case: GetSizeRecommendationUseCase) -> None:
        response = await use_case.execute("SKU1", "L")
        assert response.mismatch_rate == 0.35

    @pytest.mark.asyncio
    async def test_brand_override(self, sku_port: FakeSkuFeaturePort) -> None:
        uc = GetSizeRecommendationUseCase(
            sku_feature_port=sku_port,
            prevent_iq_engine=PreventIQEngine(),
        )
        response = await uc.execute("SKU1", "L", brand="OverrideBrand")
        assert response.recommended_size == "M"

    @pytest.mark.asyncio
    async def test_unknown_sku_uses_defaults(self, sku_port: FakeSkuFeaturePort) -> None:
        uc = GetSizeRecommendationUseCase(
            sku_feature_port=sku_port,
            prevent_iq_engine=PreventIQEngine(),
        )
        response = await uc.execute("UNKNOWN", "S")
        assert response.recommended_size == "M"
