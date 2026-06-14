# app/api/schemas/prediction_schemas.py
from __future__ import annotations

from pydantic import Field

from app.api.schemas.common import BaseSchema


class PredictReturnResponse(BaseSchema):
    return_probability: float = Field(ge=0.0, le=1.0)
    risk_level: str
    keep_rate: float = Field(ge=0.0, le=1.0)
    recommended_size: str | None = None
    size_warning: str | None = None
    category_avg_return_rate: float = Field(ge=0.0, le=1.0)


class SizeRecommendationResponse(BaseSchema):
    recommended_size: str
    confidence: float = Field(ge=0.0, le=1.0)
    current_size: str
    mismatch_rate: float = Field(ge=0.0, le=1.0)
