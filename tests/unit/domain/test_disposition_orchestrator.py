# tests/unit/domain/test_disposition_orchestrator.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.entities.condition_grade import ConditionGrade, DamageLabel
from app.domain.entities.fraud_assessment import (
    FraudAssessment,
    FraudRiskLevel,
    FraudSignal,
)
from app.domain.services.disposition_orchestrator import DispositionOrchestrator
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.demand_score import DemandScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route


def _rid() -> ReturnId:
    return ReturnId.generate()


def _mrp(v: str = "10000.00") -> Money:
    return Money.of(Decimal(v))


def _grade_entity(rid: ReturnId, grade: Grade = Grade.A) -> ConditionGrade:
    return ConditionGrade(
        return_id=rid,
        grade=grade,
        confidence=ConfidenceScore.of(92.0),
        damage_labels=[DamageLabel(name="Scratch", confidence=40.0)],
        damage_description="Minor scratch.",
        image_keys=[ImageKey.pending(rid.value, 1)],
        graded_at=datetime.now(UTC),
    )


def _fraud(rid: ReturnId, level: FraudRiskLevel = FraudRiskLevel.LOW) -> FraudAssessment:
    weight = 0 if level == FraudRiskLevel.LOW else (50 if level == FraudRiskLevel.MEDIUM else 80)
    signals = [FraudSignal(name="S", weight=weight, triggered=weight > 0, detail="x")]
    return FraudAssessment.create(
        return_id=rid, buyer_id="buyer", sku_id="SKU", signals=signals
    )


def _buyer_match(
    rid: ReturnId, p2p_recommended: bool = True, demand: int = 80
) -> BuyerMatchResult:
    return BuyerMatchResult.create(
        return_id=rid,
        sku_id="SKU",
        pincode="400001",
        grade=Grade.A,
        demand_score=DemandScore(demand),
        estimated_buyers=5,
        match_found=p2p_recommended,
        eligibility=BuyerEligibility.ELIGIBLE,
        confidence=MatchConfidence.HIGH,
        p2p_recommended=p2p_recommended,
    )


class TestDispositionOrchestrator:
    def setup_method(self) -> None:
        self.orchestrator = DispositionOrchestrator(p2p_max_radius_km=5.0)

    def test_scrap_always_wins(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.SCRAP),
            fraud_assessment=_fraud(rid, FraudRiskLevel.HIGH),
            buyer_match=_buyer_match(rid),
            mrp=_mrp(),
        )
        assert d.route == Route.SCRAP

    def test_high_fraud_overrides_to_resell(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid, FraudRiskLevel.HIGH),
            buyer_match=_buyer_match(rid),
            mrp=_mrp(),
        )
        assert d.route == Route.RESELL
        assert d.fraud_override_applied

    def test_grade_c_routes_donate(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.C),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp(),
        )
        assert d.route == Route.DONATE

    def test_grade_donate_routes_donate(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.DONATE),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp(),
        )
        assert d.route == Route.DONATE

    def test_grade_b_routes_refurbish(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.B),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp(),
        )
        assert d.route == Route.REFURBISH

    def test_grade_a_with_buyer_match_routes_p2p(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=_buyer_match(rid, p2p_recommended=True),
            mrp=_mrp(),
        )
        assert d.route == Route.P2P
        assert d.buyer_match_used

    def test_grade_a_no_buyer_match_high_demand_routes_resell(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=_buyer_match(rid, p2p_recommended=False, demand=80),
            mrp=_mrp(),
        )
        assert d.route == Route.RESELL

    def test_grade_a_no_match_low_demand_routes_resell(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp(),
        )
        assert d.route == Route.RESELL

    def test_p2p_recovery_65_pct(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=_buyer_match(rid),
            mrp=_mrp("10000.00"),
        )
        assert d.recovery_value == Money.of(Decimal("6500.00"))

    def test_resell_recovery_75_pct(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp("10000.00"),
        )
        assert d.recovery_value == Money.of(Decimal("7500.00"))

    def test_refurbish_recovery_55_pct(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.B),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp("10000.00"),
        )
        assert d.recovery_value == Money.of(Decimal("5500.00"))

    def test_donate_recovery_zero(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.C),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp("10000.00"),
        )
        assert d.recovery_value == Money.zero()

    def test_liquidation_baseline_5_pct(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp("10000.00"),
        )
        assert d.liquidation_baseline == Money.of(Decimal("500.00"))

    def test_decision_contains_demand_score(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=_buyer_match(rid, demand=75),
            mrp=_mrp(),
        )
        assert d.demand_score == 75

    def test_decision_contains_confidence(self) -> None:
        rid = _rid()
        d = self.orchestrator.decide(
            return_id=rid,
            condition_grade=_grade_entity(rid, Grade.A),
            fraud_assessment=_fraud(rid),
            buyer_match=None,
            mrp=_mrp(),
        )
        assert d.confidence == 92.0
