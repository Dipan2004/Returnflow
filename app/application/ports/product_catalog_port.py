# app/application/ports/product_catalog_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal


class ProductCatalogPort(ABC):
    """Port for fetching product metadata including MRP."""

    @abstractmethod
    async def get_mrp(self, sku_id: str) -> Decimal | None:
        """Return MRP for the SKU in INR, or None if not found."""
        ...