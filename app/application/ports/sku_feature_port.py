# app/application/ports/sku_feature_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SkuFeatures:
    category_return_rate: float
    size_mismatch_rate: float
    brand: str
    recommended_size: str
    keep_rate_for_recommended: float


class SkuFeaturePort(ABC):
    @abstractmethod
    async def get_features(self, sku_id: str, size: str) -> SkuFeatures: ...
