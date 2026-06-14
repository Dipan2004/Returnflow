# tests/fakes/fake_product_catalog_port.py
from __future__ import annotations

from decimal import Decimal

from app.application.ports.product_catalog_port import ProductCatalogPort


class FakeProductCatalogPort(ProductCatalogPort):
    """In-memory product catalog fake for tests."""

    _DEFAULT_MRP = Decimal("10000.00")

    def __init__(self, default_mrp: Decimal = _DEFAULT_MRP) -> None:
        self._default_mrp = default_mrp
        self._catalog: dict[str, Decimal] = {}

    # --- test helpers ---

    def add_sku(self, sku_id: str, mrp: Decimal) -> None:
        self._catalog[sku_id] = mrp

    def remove_sku(self, sku_id: str) -> None:
        self._catalog.pop(sku_id, None)

    # --- port implementation ---

    async def get_mrp(self, sku_id: str) -> Decimal | None:
        if sku_id in self._catalog:
            return self._catalog[sku_id]
        # If default is zero, simulate "not found"
        if self._default_mrp == Decimal("0"):
            return None
        return self._default_mrp