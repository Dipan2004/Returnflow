from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ReturnPredictionInput:
    sku_id: str
    buyer_id: str
    size: str
    brand: str
    category: str
    price_inr: float


@dataclass(frozen=True)
class ReturnPredictionResult:
    return_probability: float
    category_avg_return_rate: float
    recommended_size: str | None
    size_keep_rate: float | None
    above_category_avg: bool


class PredictionPort(ABC):
    @abstractmethod
    async def predict_return_probability(
        self,
        input_data: ReturnPredictionInput,
    ) -> ReturnPredictionResult: ...

    @abstractmethod
    async def ping_endpoint(self) -> bool: ...