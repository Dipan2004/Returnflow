from __future__ import annotations

from pydantic import Field, field_validator

from app.api.schemas.common import BaseSchema


class ReturnPredictionRequest(BaseSchema):
    sku_id: str = Field(min_length=1, max_length=100)
    buyer_id: str = Field(min_length=1, max_length=100)
    size: str = Field(min_length=1, max_length=20)
    brand: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    price_inr: float = Field(gt=0)

    @field_validator("price_inr")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v > 1_000_000:
            raise ValueError("price_inr seems unreasonably high")
        return v


class ReturnPredictionResponse(BaseSchema):
    return_probability: float = Field(ge=0.0, le=1.0)
    category_avg_return_rate: float = Field(ge=0.0, le=1.0)
    above_category_avg: bool
    size_warning: str | None = None
    recommended_size: str | None = None
    size_keep_rate: float | None = None