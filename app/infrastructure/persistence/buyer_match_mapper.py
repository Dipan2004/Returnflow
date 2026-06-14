# app/infrastructure/persistence/buyer_match_mapper.py | 72 lines
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.demand_score import DemandScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_BUYER_MATCH = "BUYER_MATCH_RESULT"


def buyer_match_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def buyer_match_sk() -> str:
    return "BUYER_MATCH"


def to_item(result: BuyerMatchResult) -> dict[str, Any]:
    return {
        "PK": buyer_match_pk(result.return_id),
        "SK": buyer_match_sk(),
        "entity_type": ENTITY_TYPE_BUYER_MATCH,
        "return_id": result.return_id.value,
        "sku_id": result.sku_id,
        "pincode": result.pincode,
        "grade": result.grade.value,
        "demand_score": result.demand_score.value,
        "demand_level": result.demand_level.value,
        "estimated_buyers": result.estimated_buyers,
        "match_found": result.match_found,
        "eligibility": result.eligibility.value,
        "confidence": result.confidence.value,
        "p2p_recommended": result.p2p_recommended,
        "computed_at": result.computed_at.isoformat(),
    }


def from_item(item: dict[str, Any]) -> BuyerMatchResult:
    return BuyerMatchResult(
        return_id=ReturnId(item["return_id"]),
        sku_id=item["sku_id"],
        pincode=item["pincode"],
        grade=Grade.from_string(item["grade"]),
        demand_score=DemandScore(int(item["demand_score"])),
        estimated_buyers=int(item["estimated_buyers"]),
        match_found=bool(item["match_found"]),
        eligibility=BuyerEligibility(item["eligibility"]),
        confidence=MatchConfidence(item["confidence"]),
        p2p_recommended=bool(item["p2p_recommended"]),
        computed_at=datetime.fromisoformat(item["computed_at"]).replace(tzinfo=UTC),
    )