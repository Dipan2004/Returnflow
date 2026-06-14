# tests/unit/application/test_get_disposition_use_case.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.use_cases.get_disposition_use_case import GetDispositionUseCase
from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from tests.fakes.fake_disposition_repository import FakeDispositionRepository


def _make_decision(
    return_id: ReturnId | None = None,
    route: Route = Route.RESELL,
    grade: Grade = Grade.A,
    mrp: Decimal = Decimal("10000.00"),
) -> DispositionDecision:
    rid = return_id or ReturnId.generate()
    mrp_money = Money.of(mrp)
    if route == Route.RESELL:
        recovery_value = mrp_money.percentage(75.0)
    else:
        recovery_value = mrp_money.percentage(55.0)
    liquidation = mrp_money.percentage(5.0)
    return DispositionDecision(
        return_id=rid,
        route=route,
        grade=grade,
        mrp=mrp_money,
        recovery_value=recovery_value,
        liquidation_baseline=liquidation,
        route_reason="test reason",
        fraud_flagged=False,
        decided_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_get_existing_disposition_returns_response() -> None:
    repo = FakeDispositionRepository()
    uc = GetDispositionUseCase(disposition_repository=repo)
    decision = _make_decision()
    await repo.save(decision)

    result = await uc.execute(decision.return_id.value)

    assert result.return_id == decision.return_id.value
    assert result.route == Route.RESELL.value
    assert result.grade == "A"
    assert result.recovery.mrp == Decimal("10000.00")
    assert result.recovery.recovery_value == Decimal("7500.00")
    assert result.recovery.liquidation_baseline == Decimal("500.00")
    assert result.recovery.value_delta == Decimal("7000.00")
    assert not result.fraud_flagged


@pytest.mark.asyncio
async def test_get_nonexistent_disposition_raises() -> None:
    repo = FakeDispositionRepository()
    uc = GetDispositionUseCase(disposition_repository=repo)

    with pytest.raises(EntityNotFoundError, match="DispositionDecision"):
        await uc.execute("NOTEXIST")


@pytest.mark.asyncio
async def test_recovery_percentage_calculated_correctly() -> None:
    repo = FakeDispositionRepository()
    uc = GetDispositionUseCase(disposition_repository=repo)
    rid = ReturnId.generate()
    mrp = Money.of(Decimal("10000.00"))
    decision = DispositionDecision(
        return_id=rid,
        route=Route.REFURBISH,
        grade=Grade.B,
        mrp=mrp,
        recovery_value=mrp.percentage(55.0),
        liquidation_baseline=mrp.percentage(5.0),
        route_reason="grade b",
        fraud_flagged=False,
        decided_at=datetime.now(UTC),
    )
    await repo.save(decision)

    result = await uc.execute(rid.value)

    assert result.recovery.recovery_percentage == pytest.approx(55.0, abs=0.1)