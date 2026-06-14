# app/infrastructure/adapters/features/in_memory_sku_features.py
from __future__ import annotations

from app.application.ports.sku_feature_port import SkuFeaturePort, SkuFeatures

_DEMO_DATA: dict[str, dict[str, SkuFeatures]] = {
    "SKU001": {
        "M": SkuFeatures(
            category_return_rate=0.18,
            size_mismatch_rate=0.10,
            brand="BrandA",
            recommended_size="M",
            keep_rate_for_recommended=0.88,
        ),
        "L": SkuFeatures(
            category_return_rate=0.18,
            size_mismatch_rate=0.30,
            brand="BrandA",
            recommended_size="M",
            keep_rate_for_recommended=0.88,
        ),
        "S": SkuFeatures(
            category_return_rate=0.18,
            size_mismatch_rate=0.35,
            brand="BrandA",
            recommended_size="M",
            keep_rate_for_recommended=0.88,
        ),
    },
    "SKU002": {
        "M": SkuFeatures(
            category_return_rate=0.25,
            size_mismatch_rate=0.05,
            brand="BrandB",
            recommended_size="M",
            keep_rate_for_recommended=0.92,
        ),
        "L": SkuFeatures(
            category_return_rate=0.25,
            size_mismatch_rate=0.08,
            brand="BrandB",
            recommended_size="L",
            keep_rate_for_recommended=0.90,
        ),
    },
    "SKU003": {
        "XL": SkuFeatures(
            category_return_rate=0.40,
            size_mismatch_rate=0.50,
            brand="BrandC",
            recommended_size="L",
            keep_rate_for_recommended=0.75,
        ),
    },
}

_DEFAULT_FEATURES = SkuFeatures(
    category_return_rate=0.20,
    size_mismatch_rate=0.15,
    brand="Unknown",
    recommended_size="M",
    keep_rate_for_recommended=0.85,
)


class InMemorySkuFeatures(SkuFeaturePort):
    async def get_features(self, sku_id: str, size: str) -> SkuFeatures:
        sku_sizes = _DEMO_DATA.get(sku_id)
        if sku_sizes is None:
            return _DEFAULT_FEATURES
        return sku_sizes.get(size, _DEFAULT_FEATURES)
