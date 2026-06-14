# tests/unit/application/test_fake_ports.py
"""Verify fake ports honour the port contracts."""
from __future__ import annotations

from decimal import Decimal

import pytest

from tests.fakes.fake_demand_signal_port import FakeDemandSignalPort
from tests.fakes.fake_disposition_repository import FakeDispositionRepository
from tests.fakes.fake_product_catalog_port import FakeProductCatalogPort


class TestFakeDemandSignalPort:
    @pytest.mark.asyncio
    async def test_default_no_demand_returns_none(self) -> None:
        port = FakeDemandSignalPort(has_demand=False)
        result = await port.get_nearest_buyer("SKU", "400001")
        assert result is None

    @pytest.mark.asyncio
    async def test_default_with_demand_returns_buyer(self) -> None:
        port = FakeDemandSignalPort(has_demand=True, buyer_id="b1", distance_km=3.0)
        result = await port.get_nearest_buyer("SKU", "400001")
        assert result == ("b1", 3.0)

    @pytest.mark.asyncio
    async def test_set_no_demand_overrides_global(self) -> None:
        port = FakeDemandSignalPort(has_demand=True)
        port.set_no_demand("SKU_A")
        result = await port.get_nearest_buyer("SKU_A", "400001")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_demand_per_sku(self) -> None:
        port = FakeDemandSignalPort(has_demand=False)
        port.set_demand("SKU_B", "buyer_2", 1.5)
        result = await port.get_nearest_buyer("SKU_B", "400001")
        assert result == ("buyer_2", 1.5)

    @pytest.mark.asyncio
    async def test_has_demand_consistent_with_get_nearest(self) -> None:
        port = FakeDemandSignalPort(has_demand=True)
        assert await port.has_demand("SKU", "400001") is True
        port.set_global_demand(has_demand=False)
        assert await port.has_demand("SKU", "400001") is False


class TestFakeProductCatalogPort:
    @pytest.mark.asyncio
    async def test_default_mrp_returned(self) -> None:
        port = FakeProductCatalogPort(default_mrp=Decimal("5000.00"))
        mrp = await port.get_mrp("ANY_SKU")
        assert mrp == Decimal("5000.00")

    @pytest.mark.asyncio
    async def test_sku_override_returned(self) -> None:
        port = FakeProductCatalogPort()
        port.add_sku("B08N5WRWNW", Decimal("12000.00"))
        mrp = await port.get_mrp("B08N5WRWNW")
        assert mrp == Decimal("12000.00")

    @pytest.mark.asyncio
    async def test_removed_sku_falls_back_to_default(self) -> None:
        port = FakeProductCatalogPort(default_mrp=Decimal("9000.00"))
        port.add_sku("SKU_X", Decimal("1000.00"))
        port.remove_sku("SKU_X")
        mrp = await port.get_mrp("SKU_X")
        assert mrp == Decimal("9000.00")

    @pytest.mark.asyncio
    async def test_zero_default_means_not_found(self) -> None:
        port = FakeProductCatalogPort(default_mrp=Decimal("0"))
        mrp = await port.get_mrp("UNKNOWN")
        assert mrp is None


class TestFakeDispositionRepository:
    @pytest.mark.asyncio
    async def test_save_and_retrieve(self) -> None:
        from datetime import UTC, datetime

        from app.domain.entities.disposition_decision import DispositionDecision
        from app.domain.value_objects.grade import Grade
        from app.domain.value_objects.money import Money
        from app.domain.value_objects.return_id import ReturnId
        from app.domain.value_objects.route import Route

        repo = FakeDispositionRepository()
        rid = ReturnId.generate()
        mrp = Money.of(Decimal("10000.00"))
        decision = DispositionDecision(
            return_id=rid,
            route=Route.RESELL,
            grade=Grade.A,
            mrp=mrp,
            recovery_value=mrp.percentage(75.0),
            liquidation_baseline=mrp.percentage(5.0),
            route_reason="test",
            fraud_flagged=False,
            decided_at=datetime.now(UTC),
        )
        await repo.save(decision)
        found = await repo.get_by_return_id(rid)
        assert found is not None
        assert found.route == Route.RESELL

    @pytest.mark.asyncio
    async def test_get_missing_returns_none(self) -> None:
        from app.domain.value_objects.return_id import ReturnId

        repo = FakeDispositionRepository()
        result = await repo.get_by_return_id(ReturnId.generate())
        assert result is None

    @pytest.mark.asyncio
    async def test_count_increments_on_save(self) -> None:
        from datetime import UTC, datetime

        from app.domain.entities.disposition_decision import DispositionDecision
        from app.domain.value_objects.grade import Grade
        from app.domain.value_objects.money import Money
        from app.domain.value_objects.return_id import ReturnId
        from app.domain.value_objects.route import Route

        repo = FakeDispositionRepository()
        mrp = Money.of(Decimal("5000.00"))
        for _ in range(3):
            rid = ReturnId.generate()
            d = DispositionDecision(
                return_id=rid,
                route=Route.DONATE,
                grade=Grade.C,
                mrp=mrp,
                recovery_value=Money.zero(),
                liquidation_baseline=mrp.percentage(5.0),
                route_reason="c",
                fraud_flagged=False,
                decided_at=datetime.now(UTC),
            )
            await repo.save(d)
        assert repo.count() == 3