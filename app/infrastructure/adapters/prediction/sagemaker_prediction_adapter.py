# app/infrastructure/adapters/prediction/sagemaker_prediction_adapter.py
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from app.application.ports.prediction_model_port import PredictionModelPort
from app.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from mypy_boto3_sagemaker_runtime import SageMakerRuntimeClient

logger = get_logger(__name__)

_DEFAULT_SCORE = 0.15


class SageMakerPredictionAdapter(PredictionModelPort):
    def __init__(self, client: SageMakerRuntimeClient, endpoint_name: str) -> None:
        self._client = client
        self._endpoint_name = endpoint_name

    async def predict(self, features: list[float]) -> float:
        try:
            payload = json.dumps({"instances": [features]})
            response: dict[str, Any] = self._client.invoke_endpoint(
                EndpointName=self._endpoint_name,
                ContentType="application/json",
                Body=payload.encode(),
            )
            body = response["Body"].read().decode()
            result = json.loads(body)
            predictions = result.get("predictions", [])
            if not predictions:
                logger.warning("SageMaker returned empty predictions, using default")
                return _DEFAULT_SCORE
            score = float(predictions[0])
            return min(max(score, 0.0), 1.0)
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("Malformed SageMaker response", error=str(exc))
            return _DEFAULT_SCORE
        except Exception as exc:
            logger.error("SageMaker invocation failed", error=str(exc))
            return _DEFAULT_SCORE
