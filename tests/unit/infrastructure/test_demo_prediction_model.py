# tests/unit/infrastructure/test_demo_prediction_model.py
from __future__ import annotations

import pytest

from app.infrastructure.adapters.prediction.demo_prediction_model import DemoPredictionModel


@pytest.fixture
def model() -> DemoPredictionModel:
    return DemoPredictionModel()


class TestDemoPredictionModel:
    @pytest.mark.asyncio
    async def test_weighted_combination(self, model: DemoPredictionModel) -> None:
        score = await model.predict([0.5, 0.5, 0.5])
        assert score == pytest.approx(0.5)

    @pytest.mark.asyncio
    async def test_all_zeros(self, model: DemoPredictionModel) -> None:
        score = await model.predict([0.0, 0.0, 0.0])
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_all_ones(self, model: DemoPredictionModel) -> None:
        score = await model.predict([1.0, 1.0, 1.0])
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_caps_at_one(self, model: DemoPredictionModel) -> None:
        score = await model.predict([2.0, 2.0, 2.0])
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_weights_correct(self, model: DemoPredictionModel) -> None:
        score = await model.predict([1.0, 0.0, 0.0])
        assert score == pytest.approx(0.4)

    @pytest.mark.asyncio
    async def test_category_weight(self, model: DemoPredictionModel) -> None:
        score = await model.predict([0.0, 1.0, 0.0])
        assert score == pytest.approx(0.3)

    @pytest.mark.asyncio
    async def test_mismatch_weight(self, model: DemoPredictionModel) -> None:
        score = await model.predict([0.0, 0.0, 1.0])
        assert score == pytest.approx(0.3)

    @pytest.mark.asyncio
    async def test_empty_features_defaults_zero(self, model: DemoPredictionModel) -> None:
        score = await model.predict([])
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_partial_features(self, model: DemoPredictionModel) -> None:
        score = await model.predict([0.5])
        assert score == pytest.approx(0.2)
