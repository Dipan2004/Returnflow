# tests/unit/application/test_buyer_match_use_cases.py | 130 lines
from __future__ import annotations

import pytest

from app.application.use_cases.buyer_match_dto import BuyerMatchRequest
from app.application.use_cases.get_buyer_match_use_case import GetBuyerMatchUseCase
from app.application.use_cases.match_buyer_use_case import MatchBuyerUseCase
from app.domain.exceptions import DomainValidationError, EntityNotFoundError
from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from tests.fakes.fake_buyer_match_repository import FakeBuyerMatchRepository
from tests.fakes.fake_buyer_matching_port import FakeBuyerMatchingPort
from tests.fakes.fake_demand_index_port import FakeDemandIndexPort


def _make_match_use_case(
    demand_score: int = 85,
    buyer_count: int = 5,
) -> tuple[MatchBuyerUseCase, FakeBuyerMatchRepository]:
    repo = FakeBuyerMatchRepository()
    demand = FakeDemandIndexPort(default_score=demand_score)
    buyers = FakeBuyerMatchingPort(default_count=buyer_count)
    engine = BuyerMatchingEngine()
    use_case = MatchBuyerUseCase(
        demand_index_port=demand,
        buyer_matching_port=buyers,
        buyer_match_repository=repo,
        buyer_matching_engine=engine,
    )
    return use_case, repo


class TestMatchBuyerUseCase:
    @pytest.mark.asyncio
    async def test_grade_a_match_found(self) -> None:
        use_case, repo = _make_match_use_case(demand_score=85, buyer_count=5)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID001", sku_id="SKU001", pincode="110001", grade="A")
        )
        assert result.match_found is True
        assert result.p2p_recommended is True
        assert result.eligibility == BuyerEligibility.ELIGIBLE.value
        assert repo.count() == 1

    @pytest.mark.asyncio
    async def test_grade_c_not_eligible(self) -> None:
        use_case, repo = _make_match_use_case(demand_score=90, buyer_count=10)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID002", sku_id="SKU001", pincode="110001", grade="C")
        )
        assert result.match_found is False
        assert result.p2p_recommended is False
        assert result.eligibility == BuyerEligibility.NOT_ELIGIBLE.value

    @pytest.mark.asyncio
    async def test_grade_b_high_demand_eligible(self) -> None:
        use_case, _ = _make_match_use_case(demand_score=90, buyer_count=3)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID003", sku_id="SKU001", pincode="110001", grade="B")
        )
        assert result.eligibility == BuyerEligibility.ELIGIBLE.value
        assert result.match_found is True

    @pytest.mark.asyncio
    async def test_grade_b_low_demand_not_eligible(self) -> None:
        use_case, _ = _make_match_use_case(demand_score=60, buyer_count=3)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID004", sku_id="SKU001", pincode="110001", grade="B")
        )
        assert result.eligibility == BuyerEligibility.NOT_ELIGIBLE.value
        assert result.match_found is False

    @pytest.mark.asyncio
    async def test_scrap_not_eligible(self) -> None:
        use_case, _ = _make_match_use_case(demand_score=100, buyer_count=10)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID005", sku_id="SKU001", pincode="110001", grade="SCRAP")
        )
        assert result.match_found is False
        assert result.eligibility == BuyerEligibility.NOT_ELIGIBLE.value

    @pytest.mark.asyncio
    async def test_demand_score_in_response(self) -> None:
        use_case, _ = _make_match_use_case(demand_score=72)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID006", sku_id="SKU001", pincode="110001", grade="A")
        )
        assert result.demand_score == 72
        assert result.demand_level == "HIGH"

    @pytest.mark.asyncio
    async def test_persists_result(self) -> None:
        use_case, repo = _make_match_use_case()
        await use_case.execute(
            BuyerMatchRequest(return_id="RID007", sku_id="SKU001", pincode="110001", grade="A")
        )
        assert repo.count() == 1

    @pytest.mark.asyncio
    async def test_invalid_grade_raises(self) -> None:
        use_case, _ = _make_match_use_case()
        with pytest.raises(DomainValidationError):
            await use_case.execute(
                BuyerMatchRequest(return_id="RID008", sku_id="SKU001", pincode="110001", grade="Z")
            )

    @pytest.mark.asyncio
    async def test_no_buyers_no_match(self) -> None:
        use_case, _ = _make_match_use_case(demand_score=85, buyer_count=0)
        result = await use_case.execute(
            BuyerMatchRequest(return_id="RID009", sku_id="SKU001", pincode="110001", grade="A")
        )
        assert result.match_found is False


class TestGetBuyerMatchUseCase:
    @pytest.mark.asyncio
    async def test_get_existing(self) -> None:
        repo = FakeBuyerMatchRepository()
        match_uc, _ = _make_match_use_case()
        match_uc._repository = repo  # type: ignore[attr-defined]
        await match_uc.execute(
            BuyerMatchRequest(return_id="RID010", sku_id="SKU001", pincode="110001", grade="A")
        )
        get_uc = GetBuyerMatchUseCase(buyer_match_repository=repo)
        result = await get_uc.execute("RID010")
        assert result.return_id == "RID010"

    @pytest.mark.asyncio
    async def test_not_found_raises(self) -> None:
        repo = FakeBuyerMatchRepository()
        get_uc = GetBuyerMatchUseCase(buyer_match_repository=repo)
        with pytest.raises(EntityNotFoundError):
            await get_uc.execute("NONEXISTENT")


class TestFakePorts:
    @pytest.mark.asyncio
    async def test_fake_demand_index_default(self) -> None:
        port = FakeDemandIndexPort(default_score=42)
        assert await port.get_demand_score("ANY") == 42

    @pytest.mark.asyncio
    async def test_fake_demand_index_set(self) -> None:
        port = FakeDemandIndexPort()
        port.set_score("SKU001", 90)
        assert await port.get_demand_score("SKU001") == 90

    @pytest.mark.asyncio
    async def test_fake_buyer_matching_default(self) -> None:
        port = FakeBuyerMatchingPort(default_count=7)
        assert await port.get_available_buyer_count("ANY", "PIN") == 7

    @pytest.mark.asyncio
    async def test_fake_buyer_matching_set(self) -> None:
        port = FakeBuyerMatchingPort()
        port.set_count("SKU001", 12)
        assert await port.get_available_buyer_count("SKU001", "110001") == 12

    @pytest.mark.asyncio
    async def test_fake_repo_save_and_get(self) -> None:
        from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
        from app.domain.value_objects.return_id import ReturnId

        repo = FakeBuyerMatchRepository()
        engine = BuyerMatchingEngine()
        rid = ReturnId.generate()
        from app.domain.value_objects.grade import Grade
        result = engine.compute(rid, "SKU001", "110001", Grade.A, 85, 5)
        await repo.save(result)
        fetched = await repo.get_by_return_id(rid)
        assert fetched is not None
        assert fetched.return_id == rid

    @pytest.mark.asyncio
    async def test_fake_repo_not_found(self) -> None:
        from app.domain.value_objects.return_id import ReturnId

        repo = FakeBuyerMatchRepository()
        result = await repo.get_by_return_id(ReturnId.generate())
        assert result is None