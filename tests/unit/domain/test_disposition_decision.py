# tests/unit/domain/test_disposition_decision.py
from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.exceptions import DomainValidationError
from app.domain.services.disposition_engine import DispositionEngine
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route


def _rid() -> ReturnId:
    return ReturnId.generate()


def _mrp(amount: str = "10000.00") -> Money:
    return Money.of(Decimal(amount))


class TestDispositionDecisionRouting:
    def test_grade_a_with_p2p_demand_routes_p2p(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=True, distance_km=2.0, matched_buyer_id="buyer_1",
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.P2P
        assert d.matched_buyer_id == "buyer_1"
        assert d.distance_km == 2.0

    def test_grade_a_no_demand_routes_resell(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.RESELL
        assert d.matched_buyer_id is None

    def test_grade_a_buyer_beyond_radius_routes_resell(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=True, distance_km=10.0, matched_buyer_id="buyer_far",
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.RESELL
        assert d.matched_buyer_id is None

    def test_grade_b_routes_refurbish(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.B, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=True, distance_km=1.0, matched_buyer_id="buyer_1",
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.REFURBISH

    def test_grade_c_routes_donate(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.C, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.DONATE

    def test_grade_donate_routes_donate(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.DONATE, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.DONATE

    def test_grade_scrap_routes_scrap(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.SCRAP, mrp=_mrp(), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.route == Route.SCRAP


class TestRecoveryValues:
    def test_p2p_recovery_is_65_pct_mrp(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=True, distance_km=1.0, matched_buyer_id="buyer_1",
            p2p_max_radius_km=5.0,
        )
        assert d.recovery_value == Money.of(Decimal("6500.00"))

    def test_resell_recovery_is_75_pct_mrp(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.recovery_value == Money.of(Decimal("7500.00"))

    def test_refurbish_recovery_is_55_pct_mrp(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.B, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.recovery_value == Money.of(Decimal("5500.00"))

    def test_donate_recovery_is_zero(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.C, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.recovery_value == Money.zero()

    def test_scrap_recovery_is_zero(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.SCRAP, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.recovery_value == Money.zero()

    def test_liquidation_baseline_is_5_pct_mrp(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.liquidation_baseline == Money.of(Decimal("500.00"))

    def test_value_delta_resell(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.A, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.value_delta == Money.of(Decimal("7000.00"))

    def test_value_delta_donate_floored_at_zero(self) -> None:
        d = DispositionDecision.decide(
            return_id=_rid(), grade=Grade.C, mrp=_mrp("10000.00"), fraud_flagged=False,
            has_p2p_match=False, distance_km=None, matched_buyer_id=None,
            p2p_max_radius_km=5.0,
        )
        assert d.value_delta == Money.zero()


class TestDispositionDecisionValidation:
    def test_p2p_without_buyer_raises(self) -> None:
        import datetime
        with pytest.raises(DomainValidationError, match="matched_buyer_id"):
            DispositionDecision(
                return_id=_rid(), route=Route.P2P, grade=Grade.A, mrp=_mrp(),
                recovery_value=_mrp("6500"), liquidation_baseline=_mrp("500"),
                route_reason="test", fraud_flagged=False,
                decided_at=datetime.datetime.now(datetime.UTC),
                matched_buyer_id=None,
            )

    def test_negative_distance_raises(self) -> None:
        import datetime
        with pytest.raises(DomainValidationError, match="distance_km"):
            DispositionDecision(
                return_id=_rid(), route=Route.RESELL, grade=Grade.A, mrp=_mrp(),
                recovery_value=_mrp("7500"), liquidation_baseline=_mrp("500"),
                route_reason="test", fraud_flagged=False,
                decided_at=datetime.datetime.now(datetime.UTC),
                distance_km=-1.0,
            )


class TestDispositionEngine:
    def setup_method(self) -> None:
        self.engine = DispositionEngine(p2p_max_radius_km=5.0)

    def test_grade_a_p2p_available_routes_p2p(self) -> None:
        d = self.engine.calculate(
            return_id=_rid(), grade=Grade.A, mrp=_mrp(),
            has_p2p_demand=True, distance_km=3.0, matched_buyer_id="buyer_1",
        )
        assert d.route == Route.P2P

    def test_grade_a_no_demand_routes_resell(self) -> None:
        d = self.engine.calculate(
            return_id=_rid(), grade=Grade.A, mrp=_mrp(),
            has_p2p_demand=False, distance_km=None, matched_buyer_id=None,
        )
        assert d.route == Route.RESELL

    def test_grade_b_routes_refurbish(self) -> None:
        d = self.engine.calculate(
            return_id=_rid(), grade=Grade.B, mrp=_mrp(),
            has_p2p_demand=True, distance_km=1.0, matched_buyer_id="buyer_1",
        )
        assert d.route == Route.REFURBISH

    def test_grade_c_routes_donate(self) -> None:
        d = self.engine.calculate(
            return_id=_rid(), grade=Grade.C, mrp=_mrp(),
            has_p2p_demand=False, distance_km=None, matched_buyer_id=None,
        )
        assert d.route == Route.DONATE

    def test_scrap_routes_scrap(self) -> None:
        d = self.engine.calculate(
            return_id=_rid(), grade=Grade.SCRAP, mrp=_mrp(),
            has_p2p_demand=False, distance_km=None, matched_buyer_id=None,
        )
        assert d.route == Route.SCRAP

    def test_invalid_radius_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            DispositionEngine(p2p_max_radius_km=-1.0)

    def test_recovery_percentage_grade_a_p2p(self) -> None:
        assert DispositionEngine.recovery_percentage_for_grade(Grade.A, has_p2p_demand=True) == 65.0

    def test_recovery_percentage_grade_a_resell(self) -> None:
        pct = DispositionEngine.recovery_percentage_for_grade(Grade.A, has_p2p_demand=False)
        assert pct == 75.0

    def test_recovery_percentage_grade_b(self) -> None:
        assert DispositionEngine.recovery_percentage_for_grade(Grade.B) == 55.0

    def test_recovery_percentage_grade_c(self) -> None:
        assert DispositionEngine.recovery_percentage_for_grade(Grade.C) == 0.0

    def test_liquidation_percentage(self) -> None:
        assert DispositionEngine.liquidation_percentage() == 5.0