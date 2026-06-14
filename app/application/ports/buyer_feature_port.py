# app/application/ports/buyer_feature_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BuyerFeatures:
    return_rate: float
    total_returns: int
    avg_days_between_returns: float
    category_preference: str


class BuyerFeaturePort(ABC):
    @abstractmethod
    async def get_features(self, buyer_id: str) -> BuyerFeatures: ...
