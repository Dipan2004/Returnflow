# tests/fakes/fake_prediction_model_port.py
from __future__ import annotations

from app.application.ports.prediction_model_port import PredictionModelPort


class FakePredictionModelPort(PredictionModelPort):
    def __init__(self, default_score: float = 0.25) -> None:
        self._score = default_score

    def set_score(self, score: float) -> None:
        self._score = score

    async def predict(self, features: list[float]) -> float:
        return self._score
