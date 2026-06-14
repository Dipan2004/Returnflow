# tests/unit/application/test_outcome_use_cases.py
from __future__ import annotations

from decimal import Decimal

import pytest

from app.application.use_cases.accept_buyer_match_use_case import AcceptBuyerMatchUseCase
from app.application.use_cases.create_outcome_use_case import CreateOutcomeUseCase
from app.application.use_cases.get_outcome_use_case import GetOutcomeUseCase
from app.application.use_cases.reject_buyer_match_use_case import RejectBuyerMatchUseCase
from app.domain.entities.disposition_outcome import DispositionOutcome
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId
from tests.fakes.fake_health_card_repository import FakeHealthCardRepository
from tests.fakes.fake_outcome_repository import FakeOutcomeRepository


@pytest.mark.asyncio
async def test_create_outcome() -> None:
    repo = FakeOutcomeRepository()
    uc = CreateOutcomeUseCase(outcome_repository=repo)
    result = await uc.execute("RET1", "buyer_1", "P2P", Decimal("6500.00"))
    assert result.status == "PENDING"
    assert repo.count() == 1


@pytest.mark.asyncio
async def test_accept_outcome() -> None:
    repo = FakeOutcomeRepository()
    hc_repo = FakeHealthCardRepository()
    rid = ReturnId("RET1")
    outcome = DispositionOutcome.create_pending(
        return_id=rid,
        buyer_id="buyer_1",
        route="P2P",
        recovery_value=Decimal("6500.00"),
    )
    await repo.save(outcome)
    uc = AcceptBuyerMatchUseCase(outcome_repository=repo, health_card_repository=hc_repo)
    result = await uc.execute("buyer_1", "RET1")
    assert result.status == "ACCEPTED"


@pytest.mark.asyncio
async def test_accept_wrong_buyer_raises() -> None:
    repo = FakeOutcomeRepository()
    hc_repo = FakeHealthCardRepository()
    rid = ReturnId("RET2")
    outcome = DispositionOutcome.create_pending(
        return_id=rid,
        buyer_id="buyer_1",
        route="P2P",
        recovery_value=Decimal("6500.00"),
    )
    await repo.save(outcome)
    uc = AcceptBuyerMatchUseCase(outcome_repository=repo, health_card_repository=hc_repo)
    with pytest.raises(DomainValidationError):
        await uc.execute("wrong_buyer", "RET2")


@pytest.mark.asyncio
async def test_reject_outcome() -> None:
    repo = FakeOutcomeRepository()
    hc_repo = FakeHealthCardRepository()
    rid = ReturnId("RET3")
    outcome = DispositionOutcome.create_pending(
        return_id=rid,
        buyer_id="buyer_1",
        route="P2P",
        recovery_value=Decimal("6500.00"),
    )
    await repo.save(outcome)
    uc = RejectBuyerMatchUseCase(outcome_repository=repo, health_card_repository=hc_repo)
    result = await uc.execute("buyer_1", "RET3", "Item not matching")
    assert result.status == "REJECTED"


@pytest.mark.asyncio
async def test_get_outcome() -> None:
    repo = FakeOutcomeRepository()
    rid = ReturnId("RET4")
    outcome = DispositionOutcome.create_pending(
        return_id=rid,
        buyer_id="buyer_1",
        route="RESELL",
        recovery_value=Decimal("7500.00"),
    )
    await repo.save(outcome)
    uc = GetOutcomeUseCase(outcome_repository=repo)
    result = await uc.execute("RET4")
    assert result.route == "RESELL"


@pytest.mark.asyncio
async def test_get_outcome_not_found() -> None:
    repo = FakeOutcomeRepository()
    uc = GetOutcomeUseCase(outcome_repository=repo)
    with pytest.raises(EntityNotFoundError):
        await uc.execute("NOTEXIST")


@pytest.mark.asyncio
async def test_accept_not_found() -> None:
    repo = FakeOutcomeRepository()
    hc_repo = FakeHealthCardRepository()
    uc = AcceptBuyerMatchUseCase(outcome_repository=repo, health_card_repository=hc_repo)
    with pytest.raises(EntityNotFoundError):
        await uc.execute("buyer", "NOTEXIST")
