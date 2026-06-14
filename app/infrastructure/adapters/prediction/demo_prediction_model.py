# app/infrastructure/adapters/prediction/demo_prediction_model.py
from __future__ import annotations

from app.application.ports.prediction_model_port import PredictionModelPort


class DemoPredictionModel(PredictionModelPort):
    async def predict(self, features: list[float]) -> float:
        buyer_return_rate = features[0] if len(features) > 0 else 0.0
        category_rate = features[1] if len(features) > 1 else 0.0
        size_mismatch = features[2] if len(features) > 2 else 0.0

        score = buyer_return_rate * 0.4 + category_rate * 0.3 + size_mismatch * 0.3
        return min(score, 1.0)
