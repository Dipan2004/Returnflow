# app/api/schemas/buyer_match_schemas.py | 48 lines
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ComputeBuyerMatchRequest(BaseModel):
    return_id: str = Field(..., min_length=1)
    sku_id: str = Field(..., min_length=1)
    pincode: str = Field(..., min_length=1)
    grade: str = Field(..., min_length=1)


class MatchedBuyer(BaseModel):
    buyer_id: str
    distance_km: float
    pincode: str


class BuyerMatchResponse(BaseModel):
    return_id: str
    sku_id: str
    pincode: str
    grade: str
    demand_score: int
    demand_level: str
    estimated_buyers: int
    match_found: bool
    eligibility: str
    confidence: str
    p2p_recommended: bool
    computed_at: datetime
    match_count: int = 0
    matched_buyers: list[MatchedBuyer] = []