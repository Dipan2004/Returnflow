# tests/unit/infrastructure/test_sagemaker_prediction_adapter.py
from __future__ import annotations

import io
import json
from unittest.mock import MagicMock

import pytest

from app.infrastructure.adapters.prediction.sagemaker_prediction_adapter import (
    SageMakerPredictionAdapter,
)


def _mock_response(body_content: str) -> dict[str, object]:
    return {"Body": io.BytesIO(body_content.encode())}


@pytest.fixture
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def adapter(mock_client: MagicMock) -> SageMakerPredictionAdapter:
    return SageMakerPredictionAdapter(client=mock_client, endpoint_name="test-endpoint")


class TestSageMakerPredictionAdapter:
    @pytest.mark.asyncio
    async def test_successful_prediction(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response(
            json.dumps({"predictions": [0.42]})
        )
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == pytest.approx(0.42)

    @pytest.mark.asyncio
    async def test_clamps_above_one(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response(
            json.dumps({"predictions": [1.5]})
        )
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_clamps_below_zero(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response(
            json.dumps({"predictions": [-0.5]})
        )
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_empty_predictions_returns_default(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response(
            json.dumps({"predictions": []})
        )
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == 0.15

    @pytest.mark.asyncio
    async def test_malformed_json_returns_default(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response("not json")
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == 0.15

    @pytest.mark.asyncio
    async def test_client_error_returns_default(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.side_effect = Exception("Connection timeout")
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == 0.15

    @pytest.mark.asyncio
    async def test_missing_predictions_key_returns_default(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response(
            json.dumps({"result": 0.5})
        )
        score = await adapter.predict([0.1, 0.2, 0.3])
        assert score == 0.15

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(
        self, adapter: SageMakerPredictionAdapter, mock_client: MagicMock
    ) -> None:
        mock_client.invoke_endpoint.return_value = _mock_response(
            json.dumps({"predictions": [0.3]})
        )
        await adapter.predict([0.5, 0.5, 0.5])
        mock_client.invoke_endpoint.assert_called_once()
        call_kwargs = mock_client.invoke_endpoint.call_args[1]
        assert call_kwargs["EndpointName"] == "test-endpoint"
        assert call_kwargs["ContentType"] == "application/json"
