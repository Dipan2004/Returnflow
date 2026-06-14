# app/domain/services/buyer_matching_engine.py | 86 lines
from __future__ import annotations

from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.demand_score import DemandScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.return_id import ReturnId

_GRADE_B_DEMAND_THRESHOLD = 80
_HIGH_DEMAND_THRESHOLD = 70
_MEDIUM_DEMAND_THRESHOLD = 40
_HIGH_BUYER_THRESHOLD = 5
_MEDIUM_BUYER_THRESHOLD = 2


class BuyerMatchingEngine:
    def compute(
        self,
        return_id: ReturnId,
        sku_id: str,
        pincode: str,
        grade: Grade,
        raw_demand_score: int,
        available_buyer_count: int,
    ) -> BuyerMatchResult:
        demand_score = DemandScore(raw_demand_score)
        eligibility = self._determine_eligibility(grade, demand_score)
        match_found = eligibility.is_eligible and available_buyer_count > 0
        confidence = self._calculate_confidence(demand_score, available_buyer_count, grade)
        p2p_recommended = match_found and eligibility.is_eligible

        return BuyerMatchResult.create(
            return_id=return_id,
            sku_id=sku_id,
            pincode=pincode,
            grade=grade,
            demand_score=demand_score,
            estimated_buyers=available_buyer_count,
            match_found=match_found,
            eligibility=eligibility,
            confidence=confidence,
            p2p_recommended=p2p_recommended,
        )

    @staticmethod
    def _determine_eligibility(grade: Grade, demand_score: DemandScore) -> BuyerEligibility:
        if grade == Grade.A:
            return BuyerEligibility.ELIGIBLE
        if grade == Grade.B and demand_score.value > _GRADE_B_DEMAND_THRESHOLD:
            return BuyerEligibility.ELIGIBLE
        return BuyerEligibility.NOT_ELIGIBLE

    @staticmethod
    def _calculate_confidence(
        demand_score: DemandScore,
        buyer_count: int,
        grade: Grade,
    ) -> MatchConfidence:
        score = 0

        if demand_score.value >= _HIGH_DEMAND_THRESHOLD:
            score += 40
        elif demand_score.value >= _MEDIUM_DEMAND_THRESHOLD:
            score += 20

        if buyer_count >= _HIGH_BUYER_THRESHOLD:
            score += 40
        elif buyer_count >= _MEDIUM_BUYER_THRESHOLD:
            score += 20

        if grade == Grade.A:
            score += 20
        elif grade == Grade.B:
            score += 10

        if score >= 80:
            return MatchConfidence.HIGH
        if score >= 40:
            return MatchConfidence.MEDIUM
        return MatchConfidence.LOW