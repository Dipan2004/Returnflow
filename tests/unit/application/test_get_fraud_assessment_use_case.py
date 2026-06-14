# tests/unit/application/test_get_fraud_assessment_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.get_fraud_assessment_use_case import GetFraudAssessmentUseCase
from app.domain.entities.fraud_assessment import FraudAssessment, FraudSignal
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId
from tests.fakes.fake_fraud_repository import FakeFraudRepository


@pytest.mark.asyncio
async def test_get_existing_assessment() -> None:
    repo = FakeFraudRepository()
    rid = ReturnId("TEST1")
    signals = [FraudSignal(name="S1", weight=20, triggered=False, detail="ok")]
    assessment = FraudAssessment.create(
        return_id=rid, buyer_id="buyer_1", sku_id="SKU_1", signals=signals
    )
    await repo.save(assessment)

    uc = GetFraudAssessmentUseCase(fraud_repository=repo)
    result = await uc.execute("TEST1")

    assert result.return_id == "TEST1"
    assert result.risk_level == "LOW"


@pytest.mark.asyncio
async def test_get_nonexistent_raises() -> None:
    repo = FakeFraudRepository()
    uc = GetFraudAssessmentUseCase(fraud_repository=repo)
    with pytest.raises(EntityNotFoundError):
        await uc.execute("NOTEXIST")


@pytest.mark.asyncio
async def test_get_returns_signals() -> None:
    repo = FakeFraudRepository()
    rid = ReturnId("TEST2")
    signals = [
        FraudSignal(name="S1", weight=30, triggered=True, detail="hit"),
        FraudSignal(name="S2", weight=25, triggered=False, detail="ok"),
    ]
    assessment = FraudAssessment.create(
        return_id=rid, buyer_id="buyer_1", sku_id="SKU_1", signals=signals
    )
    await repo.save(assessment)

    uc = GetFraudAssessmentUseCase(fraud_repository=repo)
    result = await uc.execute("TEST2")
    assert len(result.signals) == 2
    assert result.signals[0].triggered is True
    assert result.signals[1].triggered is False
