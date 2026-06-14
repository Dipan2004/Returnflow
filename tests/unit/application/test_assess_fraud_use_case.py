# tests/unit/application/test_assess_fraud_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.assess_fraud_use_case import AssessFraudUseCase
from app.application.use_cases.fraud_dto import FraudAssessmentRequest
from app.domain.services.fraud_engine import FraudEngine
from tests.fakes.fake_fraud_history_port import FakeFraudHistoryPort
from tests.fakes.fake_fraud_repository import FakeFraudRepository


def _make_use_case(
    history: FakeFraudHistoryPort | None = None,
) -> tuple[AssessFraudUseCase, FakeFraudRepository, FakeFraudHistoryPort]:
    h = history or FakeFraudHistoryPort()
    repo = FakeFraudRepository()
    engine = FraudEngine(bulk_buy_threshold=10, window_hours=72)
    uc = AssessFraudUseCase(
        fraud_history_port=h,
        fraud_repository=repo,
        fraud_engine=engine,
    )
    return uc, repo, h


@pytest.mark.asyncio
async def test_clean_buyer_returns_low_risk() -> None:
    uc, repo, _ = _make_use_case()
    result = await uc.execute(
        FraudAssessmentRequest(return_id="RET1", buyer_id="buyer_1", sku_id="SKU_1")
    )
    assert result.risk_level == "LOW"
    assert result.risk_score == 0
    assert repo.count() == 1


@pytest.mark.asyncio
async def test_risky_buyer_returns_high_risk() -> None:
    history = FakeFraudHistoryPort(
        total_returns=10, high_value_returns=5, same_sku_returns=3, returns_last_24h=4
    )
    uc, repo, _ = _make_use_case(history=history)
    result = await uc.execute(
        FraudAssessmentRequest(return_id="RET2", buyer_id="buyer_bad", sku_id="SKU_1")
    )
    assert result.risk_level == "HIGH"
    assert result.risk_score == 100


@pytest.mark.asyncio
async def test_override_included_when_high_risk_with_route() -> None:
    history = FakeFraudHistoryPort(
        total_returns=10, high_value_returns=5, same_sku_returns=3, returns_last_24h=4
    )
    uc, _, _ = _make_use_case(history=history)
    result = await uc.execute(
        FraudAssessmentRequest(
            return_id="RET3", buyer_id="buyer_bad", sku_id="SKU_1", original_route="P2P"
        )
    )
    assert result.override is not None
    assert result.override.original_route == "P2P"
    assert result.override.overridden_route == "RESELL"


@pytest.mark.asyncio
async def test_no_override_when_medium_risk() -> None:
    history = FakeFraudHistoryPort(
        total_returns=6, high_value_returns=3, same_sku_returns=0, returns_last_24h=1
    )
    uc, _, _ = _make_use_case(history=history)
    result = await uc.execute(
        FraudAssessmentRequest(
            return_id="RET4", buyer_id="buyer_med", sku_id="SKU_1", original_route="P2P"
        )
    )
    assert result.override is None
    assert result.risk_level == "MEDIUM"


@pytest.mark.asyncio
async def test_signals_returned_in_response() -> None:
    uc, _, _ = _make_use_case()
    result = await uc.execute(
        FraudAssessmentRequest(return_id="RET5", buyer_id="buyer_1", sku_id="SKU_1")
    )
    assert len(result.signals) == 4


@pytest.mark.asyncio
async def test_per_buyer_history_override() -> None:
    history = FakeFraudHistoryPort()
    history.set_history("risky_buyer", total_returns=7, high_value_returns=4,
                        same_sku_returns=2, returns_last_24h=3)
    uc, _, _ = _make_use_case(history=history)
    result = await uc.execute(
        FraudAssessmentRequest(return_id="RET6", buyer_id="risky_buyer", sku_id="SKU_1")
    )
    assert result.risk_score == 100
    assert result.risk_level == "HIGH"


@pytest.mark.asyncio
async def test_assessment_persisted() -> None:
    uc, repo, _ = _make_use_case()
    await uc.execute(
        FraudAssessmentRequest(return_id="RET7", buyer_id="buyer_1", sku_id="SKU_1")
    )
    from app.domain.value_objects.return_id import ReturnId
    saved = await repo.get_by_return_id(ReturnId("RET7"))
    assert saved is not None
    assert saved.buyer_id == "buyer_1"
