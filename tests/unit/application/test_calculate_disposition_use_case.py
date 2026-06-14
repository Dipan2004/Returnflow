# tests/unit/application/test_calculate_disposition_use_case.py
from __future__ import annotations

from decimal import Decimal

import pytest

from app.application.use_cases.calculate_disposition_use_case import (
    CalculateDispositionUseCase,
)
from app.application.use_cases.disposition_dto import DispositionRequest
from app.domain.entities.condition_grade import ConditionGrade, DamageLabel
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.services.disposition_engine import DispositionEngine
from app.domain.services.fraud_engine import FraudEngine
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from tests.factories.domain_factories import make_return_request
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.fakes.fake_demand_signal_port import FakeDemandSignalPort
from tests.fakes.fake_disposition_repository import FakeDispositionRepository
from tests.fakes.fake_fraud_history_port import FakeFraudHistoryPort
from tests.fakes.fake_fraud_repository import FakeFraudRepository
from tests.fakes.fake_product_catalog_port import FakeProductCatalogPort
from tests.fakes.fake_return_repository import FakeReturnRepository


def _make_condition_grade(return_id: ReturnId, grade: Grade = Grade.A) -> ConditionGrade:
    from datetime import UTC, datetime

    return ConditionGrade(
        return_id=return_id,
        grade=grade,
        confidence=ConfidenceScore.of(92.0),
        damage_labels=[DamageLabel(name="Scratch", confidence=45.0)],
        damage_description="Minor scratch on the back panel.",
        image_keys=[ImageKey.pending(return_id.value, 1)],
        graded_at=datetime.now(UTC),
    )


def _make_use_case(
    *,
    demand: FakeDemandSignalPort | None = None,
    catalog: FakeProductCatalogPort | None = None,
    returns: FakeReturnRepository | None = None,
    grades: FakeConditionGradeRepository | None = None,
    dispositions: FakeDispositionRepository | None = None,
    fraud_history: FakeFraudHistoryPort | None = None,
) -> tuple[
    CalculateDispositionUseCase,
    FakeReturnRepository,
    FakeConditionGradeRepository,
    FakeDispositionRepository,
    FakeDemandSignalPort,
    FakeProductCatalogPort,
]:
    r = returns or FakeReturnRepository()
    g = grades or FakeConditionGradeRepository()
    d = dispositions or FakeDispositionRepository()
    dem = demand or FakeDemandSignalPort(has_demand=False)
    cat = catalog or FakeProductCatalogPort(default_mrp=Decimal("10000.00"))
    fh = fraud_history or FakeFraudHistoryPort()
    fr = FakeFraudRepository()
    engine = DispositionEngine(p2p_max_radius_km=5.0)
    fraud_eng = FraudEngine(bulk_buy_threshold=10, window_hours=72)
    uc = CalculateDispositionUseCase(
        return_repository=r,
        condition_grade_repository=g,
        disposition_repository=d,
        demand_signal_port=dem,
        product_catalog_port=cat,
        disposition_engine=engine,
        fraud_history_port=fh,
        fraud_repository=fr,
        fraud_engine=fraud_eng,
    )
    return uc, r, g, d, dem, cat


@pytest.mark.asyncio
async def test_calculate_grade_a_no_demand_routes_resell() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    cg = _make_condition_grade(rr.return_id, Grade.A)
    await g.save(cg)

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
        )
    )

    assert result.route == Route.RESELL.value
    assert result.grade == "A"
    assert d.count() == 1


@pytest.mark.asyncio
async def test_calculate_grade_a_with_demand_routes_p2p() -> None:
    demand = FakeDemandSignalPort(has_demand=True, buyer_id="buyer_near", distance_km=2.0)
    uc, r, g, d, _, _ = _make_use_case(demand=demand)
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.A))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
        )
    )

    assert result.route == Route.P2P.value
    assert result.matched_buyer_id == "buyer_near"
    assert result.distance_km == 2.0


@pytest.mark.asyncio
async def test_calculate_grade_b_routes_refurbish() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.B))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
        )
    )

    assert result.route == Route.REFURBISH.value


@pytest.mark.asyncio
async def test_calculate_grade_c_routes_donate() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.C))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
        )
    )

    assert result.route == Route.DONATE.value


@pytest.mark.asyncio
async def test_calculate_grade_scrap_routes_scrap() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.SCRAP))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
        )
    )

    assert result.route == Route.SCRAP.value


@pytest.mark.asyncio
async def test_mrp_from_catalog_used_when_not_in_request() -> None:
    catalog = FakeProductCatalogPort(default_mrp=Decimal("5000.00"))
    uc, r, g, d, _, _ = _make_use_case(catalog=catalog)
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.A))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="SOMESKU",
            seller_pincode="400001",
        )
    )

    # 75% of 5000 = 3750
    assert result.recovery.mrp == Decimal("5000.00")
    assert result.recovery.recovery_value == Decimal("3750.00")


@pytest.mark.asyncio
async def test_mrp_override_in_request_used() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.A))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
            mrp=Decimal("20000.00"),
        )
    )

    # 75% of 20000 = 15000
    assert result.recovery.mrp == Decimal("20000.00")
    assert result.recovery.recovery_value == Decimal("15000.00")


@pytest.mark.asyncio
async def test_recovery_breakdown_liquidation_and_delta() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.A))

    result = await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
            mrp=Decimal("10000.00"),
        )
    )

    assert result.recovery.liquidation_baseline == Decimal("500.00")
    assert result.recovery.value_delta == Decimal("7000.00")


@pytest.mark.asyncio
async def test_return_not_found_raises() -> None:
    uc, _, _, _, _, _ = _make_use_case()
    with pytest.raises(EntityNotFoundError, match="ReturnRequest"):
        await uc.execute(
            DispositionRequest(
                return_id="NOTEXIST",
                sku_id="B08N5WRWNW",
                seller_pincode="400001",
            )
        )


@pytest.mark.asyncio
async def test_condition_grade_not_found_raises() -> None:
    uc, r, _, _, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    # Do NOT save a condition grade
    with pytest.raises(EntityNotFoundError, match="ConditionGrade"):
        await uc.execute(
            DispositionRequest(
                return_id=rr.return_id.value,
                sku_id="B08N5WRWNW",
                seller_pincode="400001",
            )
        )


@pytest.mark.asyncio
async def test_sku_not_in_catalog_raises() -> None:
    catalog = FakeProductCatalogPort(default_mrp=Decimal("0"))
    uc, r, g, _, _, _ = _make_use_case(catalog=catalog)
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.A))

    with pytest.raises(DomainValidationError, match="MRP not found"):
        await uc.execute(
            DispositionRequest(
                return_id=rr.return_id.value,
                sku_id="UNKNOWN_SKU",
                seller_pincode="400001",
            )
        )


@pytest.mark.asyncio
async def test_decision_persisted_to_repository() -> None:
    uc, r, g, d, _, _ = _make_use_case()
    rr = make_return_request()
    await r.save(rr)
    await g.save(_make_condition_grade(rr.return_id, Grade.B))

    await uc.execute(
        DispositionRequest(
            return_id=rr.return_id.value,
            sku_id="B08N5WRWNW",
            seller_pincode="400001",
            mrp=Decimal("8000.00"),
        )
    )

    assert d.count() == 1
    saved = d.all()[0]
    assert saved.route == Route.REFURBISH