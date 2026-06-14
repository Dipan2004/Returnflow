# tests/unit/infrastructure/test_disposition_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from app.infrastructure.persistence.disposition_mapper import from_item, to_item


def _make_decision(
    route: Route = Route.RESELL,
    grade: Grade = Grade.A,
    mrp: Decimal = Decimal("10000.00"),
    matched_buyer_id: str | None = None,
    distance_km: float | None = None,
) -> DispositionDecision:
    rid = ReturnId.generate()
    mrp_money = Money.of(mrp)
    recovery = mrp_money.percentage(75.0)
    liq = mrp_money.percentage(5.0)
    return DispositionDecision(
        return_id=rid,
        route=route,
        grade=grade,
        mrp=mrp_money,
        recovery_value=recovery,
        liquidation_baseline=liq,
        route_reason="test",
        fraud_flagged=False,
        decided_at=datetime.now(UTC),
        matched_buyer_id=matched_buyer_id,
        distance_km=distance_km,
    )


def test_to_item_contains_required_keys() -> None:
    d = _make_decision()
    item = to_item(d)
    for key in ("PK", "SK", "entity_type", "return_id", "route", "grade",
                "mrp_amount", "recovery_value_amount", "liquidation_baseline_amount",
                "value_delta_amount", "route_reason", "fraud_flagged", "decided_at"):
        assert key in item


def test_round_trip_without_buyer() -> None:
    original = _make_decision()
    item = to_item(original)
    restored = from_item(item)

    assert restored.return_id == original.return_id
    assert restored.route == original.route
    assert restored.grade == original.grade
    assert restored.mrp == original.mrp
    assert restored.recovery_value == original.recovery_value
    assert restored.matched_buyer_id is None
    assert restored.distance_km is None


def test_round_trip_with_p2p_buyer() -> None:
    rid = ReturnId.generate()
    mrp = Money.of(Decimal("10000.00"))
    original = DispositionDecision(
        return_id=rid,
        route=Route.P2P,
        grade=Grade.A,
        mrp=mrp,
        recovery_value=mrp.percentage(65.0),
        liquidation_baseline=mrp.percentage(5.0),
        route_reason="p2p test",
        fraud_flagged=False,
        decided_at=datetime.now(UTC),
        matched_buyer_id="buyer_xyz",
        distance_km=1.8,
    )
    item = to_item(original)
    restored = from_item(item)

    assert restored.matched_buyer_id == "buyer_xyz"
    assert restored.distance_km == 1.8
    assert restored.route == Route.P2P


def test_round_trip_fraud_flagged() -> None:
    rid = ReturnId.generate()
    mrp = Money.of(Decimal("10000.00"))
    original = DispositionDecision(
        return_id=rid,
        route=Route.RESELL,
        grade=Grade.A,
        mrp=mrp,
        recovery_value=mrp.percentage(75.0),
        liquidation_baseline=mrp.percentage(5.0),
        route_reason="fraud override",
        fraud_flagged=True,
        decided_at=datetime.now(UTC),
    )
    item = to_item(original)
    restored = from_item(item)

    assert restored.fraud_flagged is True


def test_sk_is_disposition() -> None:
    d = _make_decision()
    item = to_item(d)
    assert item["SK"] == "DISPOSITION"


def test_pk_contains_return_id() -> None:
    d = _make_decision()
    item = to_item(d)
    assert item["PK"] == f"RETURN#{d.return_id.value}"