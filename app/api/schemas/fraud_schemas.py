# app/api/schemas/fraud_schemas.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FraudSignalResponse(BaseModel):
    name: str
    weight: int
    triggered: bool
    detail: str


class FraudOverrideResponse(BaseModel):
    original_route: str
    overridden_route: str
    risk_level: str
    risk_score: int
    reason: str


class AssessFraudRequest(BaseModel):
    return_id: str = Field(min_length=1)
    buyer_id: str = Field(min_length=1)
    sku_id: str = Field(min_length=1)
    original_route: str | None = None


class FraudAssessmentResponse(BaseModel):
    return_id: str
    buyer_id: str
    sku_id: str
    risk_score: int
    risk_level: str
    signals: list[FraudSignalResponse]
    override: FraudOverrideResponse | None = None
    assessed_at: datetime
