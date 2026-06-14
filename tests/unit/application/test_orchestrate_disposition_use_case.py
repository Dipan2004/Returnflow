# tests/unit/application/test_orchestrate_disposition_use_case.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.use_cases.orchestrate_disposition_use_case import (
    OrchestrateDispositionUseCase,
)
from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.entities.condition_grade import ConditionGrade, DamageLabel
from app.domain.entities.fraud_assessment import FraudAssessment, FraudSignal
from app.domain.exceptions import EntityNotFoundError
from app.domain.services.disposition_orchestrator import DispositionOrchestrator
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.demand_score import DemandScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from tests.factories.domain_factories import make_return_request
from tests.fakes.fake_buyer_match_repository import FakeBuyerMatchRepository
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.fakes.fake_disposition_repository import FakeDispositionRepository
from tests.fakes.fake_fraud_repository import FakeFraudRepository
from tests.fakes.fake_product_catalog_port import FakeProductCatalogPort
from tests.fakes.fake_return_repository import FakeReturnRepository


def _make_use_case() -> tuple[
    OrchestrateDispositionUseCase,
    FakeReturnRepository,
    FakeConditionGradeRepository,
    FakeFraudRepository,
    FakeBuyerMatchRepository,
    FakeDispositionRepository,
    FakeProductCatalogPort,
]:
    returns = FakeReturnRepository()
    grades = FakeConditionGradeRepository()
    fraud = FakeFraudRepository()
    buyer = FakeBuyerMatchRepository()
    dispositions = FakeDispositionRepository()
    catalog = FakeProductCatalogPort(default_mrp=Decimal("10000.00"))
    orchestrator = DispositionOrchestrator(p2p_max_radius_km=5.0)
    uc = OrchestrateDispositionUseCase(
        return_repository=returns,
        condition_grade_repository=grades,
        fraud_repository=fraud,
        buyer_match_repository=buyer,
        disposition_repository=dispositions,
        product_catalog_port=catalog,
        orchestrator=orchestrator,
    )
    return uc, returns, grades, fraud, buyer, dispositions, catalog


def _make_grade(rid: ReturnId, grade: Grade = Grade.A) -> ConditionGrade:
    return ConditionGrade(
        return_id=rid,
        grade=grade,
        confidence=ConfidenceScore.of(92.0),
        damage_labels=[DamageLabel(name="Scratch", confidence=40.0)],
        damage_description="Minor scratch.",
        image_keys=[ImageKey.pending(rid.value, 1)],
        graded_at=datetime.now(UTC),
    )


def _make_fraud(rid: ReturnId, high: bool = False) -> FraudAssessment:
    weight = 80 if high else 0
    signals = [FraudSignal(name="S", weight=weight, triggered=high, detail="x")]
    return FraudAssessment.create(
        return_id=rid, buyer_id="buyer", sku_id="SKU", signals=signals
    )


def _make_buyer_match(rid: ReturnId, p2p: bool = True) -> BuyerMatchResult:
    return BuyerMatchResult.create(
        return_id=rid,
        sku_id="SKU",
        pincode="400001",
        grade=Grade.A,
        demand_score=DemandScore(80),
        estimated_buyers=5,
        match_found=p2p,
        eligibility=BuyerEligibility.ELIGIBLE,
        confidence=MatchConfidence.HIGH,
        p2p_recommended=p2p,
    )


@pytest.mark.asyncio
async def test_grade_a_p2p_match_routes_p2p() -> None:
    uc, returns, grades, fraud, buyer, dispositions, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.A))
    await fraud.save(_make_fraud(rr.return_id))
    await buyer.save(_make_buyer_match(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.route == "P2P"
    assert result.buyer_match_used
    assert not result.fraud_override_applied
    assert dispositions.count() == 1


@pytest.mark.asyncio
async def test_grade_a_fraud_high_overrides_to_resell() -> None:
    uc, returns, grades, fraud, buyer, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.A))
    await fraud.save(_make_fraud(rr.return_id, high=True))
    await buyer.save(_make_buyer_match(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.route == "RESELL"
    assert result.fraud_override_applied
    assert not result.buyer_match_used


@pytest.mark.asyncio
async def test_grade_b_routes_refurbish() -> None:
    uc, returns, grades, fraud, _, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.B))
    await fraud.save(_make_fraud(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.route == "REFURBISH"


@pytest.mark.asyncio
async def test_grade_c_routes_donate() -> None:
    uc, returns, grades, fraud, _, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.C))
    await fraud.save(_make_fraud(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.route == "DONATE"


@pytest.mark.asyncio
async def test_scrap_routes_scrap() -> None:
    uc, returns, grades, fraud, _, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.SCRAP))
    await fraud.save(_make_fraud(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.route == "SCRAP"


@pytest.mark.asyncio
async def test_return_not_found_raises() -> None:
    uc, _, _, _, _, _, _ = _make_use_case()
    with pytest.raises(EntityNotFoundError):
        await uc.execute("NOTEXIST")


@pytest.mark.asyncio
async def test_grade_not_found_raises() -> None:
    uc, returns, _, _, _, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    with pytest.raises(EntityNotFoundError):
        await uc.execute(rr.return_id.value)


@pytest.mark.asyncio
async def test_fraud_not_found_raises() -> None:
    uc, returns, grades, _, _, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id))
    with pytest.raises(EntityNotFoundError):
        await uc.execute(rr.return_id.value)


@pytest.mark.asyncio
async def test_no_buyer_match_grade_a_routes_resell() -> None:
    uc, returns, grades, fraud, _, _, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.A))
    await fraud.save(_make_fraud(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.route == "RESELL"
    assert not result.buyer_match_used


@pytest.mark.asyncio
async def test_recovery_value_persisted() -> None:
    uc, returns, grades, fraud, buyer, dispositions, _ = _make_use_case()
    rr = make_return_request()
    await returns.save(rr)
    await grades.save(_make_grade(rr.return_id, Grade.A))
    await fraud.save(_make_fraud(rr.return_id))
    await buyer.save(_make_buyer_match(rr.return_id))

    result = await uc.execute(rr.return_id.value)

    assert result.recovery_value == Decimal("6500.00")
    saved = dispositions.all()[0]
    assert saved.recovery_value == Money.of(Decimal("6500.00"))
