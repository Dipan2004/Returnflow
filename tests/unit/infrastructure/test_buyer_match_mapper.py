# tests/unit/infrastructure/test_buyer_match_mapper.py | 80 lines
from __future__ import annotations

import pytest

from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.adapters.buyer_match.in_memory_buyer_matching_adapter import (
    InMemoryBuyerMatchingAdapter,
)
from app.infrastructure.adapters.buyer_match.in_memory_demand_index import InMemoryDemandIndex
from app.infrastructure.persistence.buyer_match_mapper import from_item, to_item


def _make_result() -> object:
    engine = BuyerMatchingEngine()
    rid = ReturnId.generate()
    return engine.compute(rid, "SKU001", "110001", Grade.A, 85, 5)


class TestBuyerMatchMapper:
    def test_roundtrip(self) -> None:
        result = _make_result()
        item = to_item(result)  # type: ignore[arg-type]
        restored = from_item(item)
        assert restored.return_id == result.return_id  # type: ignore[union-attr]
        assert restored.sku_id == result.sku_id  # type: ignore[union-attr]
        assert restored.pincode == result.pincode  # type: ignore[union-attr]
        assert restored.grade == result.grade  # type: ignore[union-attr]
        assert restored.demand_score == result.demand_score  # type: ignore[union-attr]
        assert restored.estimated_buyers == result.estimated_buyers  # type: ignore[union-attr]
        assert restored.match_found == result.match_found  # type: ignore[union-attr]
        assert restored.eligibility == result.eligibility  # type: ignore[union-attr]
        assert restored.confidence == result.confidence  # type: ignore[union-attr]
        assert restored.p2p_recommended == result.p2p_recommended  # type: ignore[union-attr]

    def test_item_has_pk_sk(self) -> None:
        result = _make_result()
        item = to_item(result)  # type: ignore[arg-type]
        assert item["PK"].startswith("RETURN#")
        assert item["SK"] == "BUYER_MATCH"

    def test_item_entity_type(self) -> None:
        result = _make_result()
        item = to_item(result)  # type: ignore[arg-type]
        assert item["entity_type"] == "BUYER_MATCH_RESULT"

    def test_from_item_grade_a(self) -> None:
        result = _make_result()
        item = to_item(result)  # type: ignore[arg-type]
        restored = from_item(item)
        assert restored.grade == Grade.A

    def test_from_item_eligibility(self) -> None:
        result = _make_result()
        item = to_item(result)  # type: ignore[arg-type]
        restored = from_item(item)
        assert restored.eligibility == BuyerEligibility.ELIGIBLE

    def test_from_item_confidence(self) -> None:
        result = _make_result()
        item = to_item(result)  # type: ignore[arg-type]
        restored = from_item(item)
        assert restored.confidence in list(MatchConfidence)


class TestInMemoryDemandIndex:
    @pytest.mark.asyncio
    async def test_sku001_returns_85(self) -> None:
        idx = InMemoryDemandIndex()
        assert await idx.get_demand_score("SKU001") == 85

    @pytest.mark.asyncio
    async def test_sku002_returns_72(self) -> None:
        idx = InMemoryDemandIndex()
        assert await idx.get_demand_score("SKU002") == 72

    @pytest.mark.asyncio
    async def test_sku003_returns_25(self) -> None:
        idx = InMemoryDemandIndex()
        assert await idx.get_demand_score("SKU003") == 25

    @pytest.mark.asyncio
    async def test_unknown_sku_returns_default(self) -> None:
        idx = InMemoryDemandIndex()
        score = await idx.get_demand_score("UNKNOWN_SKU")
        assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_buyer_matching_sku001(self) -> None:
        adapter = InMemoryBuyerMatchingAdapter()
        count = await adapter.get_available_buyer_count("SKU001", "110001")
        assert count == 8

    @pytest.mark.asyncio
    async def test_buyer_matching_sku003_zero(self) -> None:
        adapter = InMemoryBuyerMatchingAdapter()
        count = await adapter.get_available_buyer_count("SKU003", "110001")
        assert count == 0

    @pytest.mark.asyncio
    async def test_buyer_matching_unknown_sku_default(self) -> None:
        adapter = InMemoryBuyerMatchingAdapter()
        count = await adapter.get_available_buyer_count("UNKNOWN", "110001")
        assert count >= 0