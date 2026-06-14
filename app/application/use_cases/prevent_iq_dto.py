# app/application/use_cases/prevent_iq_dto.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictReturnRequest:
    buyer_id: str
    sku_id: str
    size: str
    brand: str | None = None


@dataclass(frozen=True)
class PredictReturnResponse:
    return_probability: float
    risk_level: str
    keep_rate: float
    recommended_size: str | None
    size_warning: str | None
    category_avg_return_rate: float


@dataclass(frozen=True)
class SizeRecommendationResponse:
    recommended_size: str
    confidence: float
    current_size: str
    mismatch_rate: float
