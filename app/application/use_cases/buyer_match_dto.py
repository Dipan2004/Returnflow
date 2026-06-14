# app/application/use_cases/buyer_match_dto.py | 52 lines
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BuyerMatchRequest:
    return_id: str
    sku_id: str
    pincode: str
    grade: str


@dataclass(frozen=True)
class BuyerMatchResponse:
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


@dataclass(frozen=True)
class BuyerMatchSummary:
    return_id: str
    match_found: bool
    p2p_recommended: bool
    demand_level: str
    confidence: str