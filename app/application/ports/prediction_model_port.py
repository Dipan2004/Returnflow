# app/application/ports/prediction_model_port.py
from __future__ import annotations

from abc import ABC, abstractmethod


class PredictionModelPort(ABC):
    @abstractmethod
    async def predict(self, features: list[float]) -> float: ...
