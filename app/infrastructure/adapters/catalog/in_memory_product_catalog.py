# app/infrastructure/adapters/catalog/in_memory_product_catalog.py
from __future__ import annotations

from decimal import Decimal

from app.application.ports.product_catalog_port import ProductCatalogPort

_DEFAULT_CATALOG: dict[str, Decimal] = {
    "B08N5WRWNW": Decimal("850.00"),
    "B09XYZ1234": Decimal("1299.00"),
    "B07ABC5678": Decimal("499.00"),
}

_FALLBACK_MRP = Decimal("999.00")


class InMemoryProductCatalog(ProductCatalogPort):
    def __init__(self, fallback_mrp: Decimal = _FALLBACK_MRP) -> None:
        self._catalog: dict[str, Decimal] = dict(_DEFAULT_CATALOG)
        self._fallback = fallback_mrp

    async def get_mrp(self, sku_id: str) -> Decimal | None:
        return self._catalog.get(sku_id, self._fallback)
