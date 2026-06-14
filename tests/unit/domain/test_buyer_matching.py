# tests/unit/domain/test_buyer_matching.py | 180 lines
from __future__ import annotations

import pytest

from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.exceptions import DomainValidationError
from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.demand_level import DemandLevel
from app.domain.value_objects.demand_score import DemandScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.return_id import ReturnId


def _rid() -> ReturnId:
    return ReturnId.generate()


class TestDemandScore:
    def test_valid_score(self) -> None:
        ds = DemandScore(85)
        assert ds.value == 85

    def test_zero(self) -> None:
        ds = DemandScore(0)
        assert ds.value == 0

    def test_hundred(self) -> None:
        ds = DemandScore(100)
        assert ds.value == 100

    def test_below_zero_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            DemandScore(-1)

    def test_above_hundred_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            DemandScore(101)

    def test_level_low(self) -> None:
        assert DemandScore(0).level == DemandLevel.LOW
        assert DemandScore(39).level == DemandLevel.LOW

    def test_level_medium(self) -> None:
        assert DemandScore(40).level == DemandLevel.MEDIUM
        assert DemandScore(69).level == DemandLevel.MEDIUM

    def test_level_high(self) -> None:
        assert DemandScore(70).level == DemandLevel.HIGH
        assert DemandScore(100).level == DemandLevel.HIGH

    def test_equality(self) -> None:
        assert DemandScore(50) == DemandScore(50)
        assert DemandScore(50) != DemandScore(60)


class TestBuyerEligibility:
    def test_eligible_is_eligible(self) -> None:
        assert BuyerEligibility.ELIGIBLE.is_eligible is True

    def test_not_eligible(self) -> None:
        assert BuyerEligibility.NOT_ELIGIBLE.is_eligible is False


class TestBuyerMatchResult:
    def test_create(self) -> None:
        rid = _rid()
        result = BuyerMatchResult.create(
            return_id=rid,
            sku_id="SKU001",
            pincode="110001",
            grade=Grade.A,
            demand_score=DemandScore(85),
            estimated_buyers=5,
            match_found=True,
            eligibility=BuyerEligibility.ELIGIBLE,
            confidence=MatchConfidence.HIGH,
            p2p_recommended=True,
        )
        assert result.return_id == rid
        assert result.sku_id == "SKU001"
        assert result.grade == Grade.A
        assert result.demand_level == DemandLevel.HIGH

    def test_empty_sku_raises(self) -> None:
        from datetime import UTC, datetime

        with pytest.raises(DomainValidationError):
            BuyerMatchResult(
                return_id=_rid(),
                sku_id="",
                pincode="110001",
                grade=Grade.A,
                demand_score=DemandScore(50),
                estimated_buyers=1,
                match_found=True,
                eligibility=BuyerEligibility.ELIGIBLE,
                confidence=MatchConfidence.MEDIUM,
                p2p_recommended=True,
                computed_at=datetime.now(UTC),
            )

    def test_empty_pincode_raises(self) -> None:
        from datetime import UTC, datetime

        with pytest.raises(DomainValidationError):
            BuyerMatchResult(
                return_id=_rid(),
                sku_id="SKU001",
                pincode="",
                grade=Grade.A,
                demand_score=DemandScore(50),
                estimated_buyers=1,
                match_found=True,
                eligibility=BuyerEligibility.ELIGIBLE,
                confidence=MatchConfidence.MEDIUM,
                p2p_recommended=True,
                computed_at=datetime.now(UTC),
            )

    def test_negative_buyers_raises(self) -> None:
        from datetime import UTC, datetime

        with pytest.raises(DomainValidationError):
            BuyerMatchResult(
                return_id=_rid(),
                sku_id="SKU001",
                pincode="110001",
                grade=Grade.A,
                demand_score=DemandScore(50),
                estimated_buyers=-1,
                match_found=False,
                eligibility=BuyerEligibility.NOT_ELIGIBLE,
                confidence=MatchConfidence.LOW,
                p2p_recommended=False,
                computed_at=datetime.now(UTC),
            )

    def test_equality_by_return_id(self) -> None:
        rid = _rid()
        r1 = BuyerMatchResult.create(
            return_id=rid, sku_id="SKU001", pincode="110001", grade=Grade.A,
            demand_score=DemandScore(85), estimated_buyers=5, match_found=True,
            eligibility=BuyerEligibility.ELIGIBLE, confidence=MatchConfidence.HIGH,
            p2p_recommended=True,
        )
        r2 = BuyerMatchResult.create(
            return_id=rid, sku_id="SKU002", pincode="110002", grade=Grade.B,
            demand_score=DemandScore(30), estimated_buyers=0, match_found=False,
            eligibility=BuyerEligibility.NOT_ELIGIBLE, confidence=MatchConfidence.LOW,
            p2p_recommended=False,
        )
        assert r1 == r2


class TestBuyerMatchingEngine:
    def setup_method(self) -> None:
        self.engine = BuyerMatchingEngine()

    def test_grade_a_eligible(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.A, 50, 3)
        assert result.eligibility == BuyerEligibility.ELIGIBLE

    def test_grade_b_eligible_high_demand(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.B, 85, 3)
        assert result.eligibility == BuyerEligibility.ELIGIBLE

    def test_grade_b_not_eligible_low_demand(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.B, 80, 3)
        assert result.eligibility == BuyerEligibility.NOT_ELIGIBLE

    def test_grade_c_not_eligible(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.C, 95, 10)
        assert result.eligibility == BuyerEligibility.NOT_ELIGIBLE

    def test_scrap_not_eligible(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.SCRAP, 95, 10)
        assert result.eligibility == BuyerEligibility.NOT_ELIGIBLE

    def test_match_found_grade_a_with_buyers(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.A, 85, 5)
        assert result.match_found is True
        assert result.p2p_recommended is True

    def test_no_match_grade_a_no_buyers(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.A, 85, 0)
        assert result.match_found is False
        assert result.p2p_recommended is False

    def test_confidence_high(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.A, 85, 8)
        assert result.confidence == MatchConfidence.HIGH

    def test_confidence_low(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.C, 20, 0)
        assert result.confidence == MatchConfidence.LOW

    def test_demand_score_stored(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.A, 72, 3)
        assert result.demand_score.value == 72
        assert result.demand_level == DemandLevel.HIGH

    def test_repr(self) -> None:
        result = self.engine.compute(_rid(), "SKU001", "110001", Grade.A, 85, 5)
        assert "BuyerMatchResult" in repr(result)