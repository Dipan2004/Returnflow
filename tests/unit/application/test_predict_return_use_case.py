# tests/unit/application/test_predict_return_use_case.py
from __future__ import annotations

import pytest

from app.application.ports.buyer_feature_port import BuyerFeatures
from app.application.ports.sku_feature_port import SkuFeatures
from app.application.use_cases.predict_return_use_case import PredictReturnUseCase
from app.application.use_cases.prevent_iq_dto import PredictReturnRequest
from app.domain.services.prevent_iq_engine import PreventIQEngine
from tests.fakes.fake_buyer_feature_port import FakeBuyerFeaturePort
from tests.fakes.fake_prediction_model_port import FakePredictionModelPort
from tests.fakes.fake_sku_feature_port import FakeSkuFeaturePort


@pytest.fixture
def buyer_port() -> FakeBuyerFeaturePort:
    port = FakeBuyerFeaturePort()
    port.set_features(
        "BUYER1",
        BuyerFeatures(
            return_rate=0.20,
            total_returns=5,
            avg_days_between_returns=20.0,
            category_preference="apparel",
        ),
    )
    return port


@pytest.fixture
def sku_port() -> FakeSkuFeaturePort:
    port = FakeSkuFeaturePort()
    port.set_features(
        "SKU1",
        "M",
        SkuFeatures(
            category_return_rate=0.25,
            size_mismatch_rate=0.30,
            brand="TestBrand",
            recommended_size="L",
            keep_rate_for_recommended=0.90,
        ),
    )
    return port


@pytest.fixture
def model_port() -> FakePredictionModelPort:
    return FakePredictionModelPort(default_score=0.35)


@pytest.fixture
def use_case(
    buyer_port: FakeBuyerFeaturePort,
    sku_port: FakeSkuFeaturePort,
    model_port: FakePredictionModelPort,
) -> PredictReturnUseCase:
    return PredictReturnUseCase(
        buyer_feature_port=buyer_port,
        sku_feature_port=sku_port,
        prediction_model=model_port,
        prevent_iq_engine=PreventIQEngine(),
    )


class TestPredictReturnUseCase:
    @pytest.mark.asyncio
    async def test_returns_probability(self, use_case: PredictReturnUseCase) -> None:
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await use_case.execute(request)
        assert response.return_probability == 0.35

    @pytest.mark.asyncio
    async def test_risk_level_medium(self, use_case: PredictReturnUseCase) -> None:
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await use_case.execute(request)
        assert response.risk_level == "MEDIUM"

    @pytest.mark.asyncio
    async def test_size_warning_present(self, use_case: PredictReturnUseCase) -> None:
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await use_case.execute(request)
        assert response.size_warning is not None

    @pytest.mark.asyncio
    async def test_keep_rate(self, use_case: PredictReturnUseCase) -> None:
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await use_case.execute(request)
        assert response.keep_rate == 0.90

    @pytest.mark.asyncio
    async def test_category_avg_return_rate(self, use_case: PredictReturnUseCase) -> None:
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await use_case.execute(request)
        assert response.category_avg_return_rate == 0.25

    @pytest.mark.asyncio
    async def test_recommended_size(self, use_case: PredictReturnUseCase) -> None:
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await use_case.execute(request)
        assert response.recommended_size == "L"

    @pytest.mark.asyncio
    async def test_low_risk_with_low_score(
        self,
        buyer_port: FakeBuyerFeaturePort,
        sku_port: FakeSkuFeaturePort,
    ) -> None:
        model = FakePredictionModelPort(default_score=0.10)
        uc = PredictReturnUseCase(
            buyer_feature_port=buyer_port,
            sku_feature_port=sku_port,
            prediction_model=model,
            prevent_iq_engine=PreventIQEngine(),
        )
        request = PredictReturnRequest(buyer_id="BUYER1", sku_id="SKU1", size="M")
        response = await uc.execute(request)
        assert response.risk_level == "LOW"

    @pytest.mark.asyncio
    async def test_unknown_buyer_uses_defaults(
        self,
        sku_port: FakeSkuFeaturePort,
        model_port: FakePredictionModelPort,
    ) -> None:
        buyer_port = FakeBuyerFeaturePort()
        uc = PredictReturnUseCase(
            buyer_feature_port=buyer_port,
            sku_feature_port=sku_port,
            prediction_model=model_port,
            prevent_iq_engine=PreventIQEngine(),
        )
        request = PredictReturnRequest(buyer_id="UNKNOWN", sku_id="SKU1", size="M")
        response = await uc.execute(request)
        assert response.return_probability == 0.35
