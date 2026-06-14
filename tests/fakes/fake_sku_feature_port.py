# tests/fakes/fake_sku_feature_port.py
from __future__ import annotations

from app.application.ports.sku_feature_port import SkuFeaturePort, SkuFeatures

_DEFAULT = SkuFeatures(
    category_return_rate=0.20,
    size_mismatch_rate=0.15,
    brand="TestBrand",
    recommended_size="M",
    keep_rate_for_recommended=0.85,
)


class FakeSkuFeaturePort(SkuFeaturePort):
    def __init__(self, default: SkuFeatures = _DEFAULT) -> None:
        self._data: dict[tuple[str, str], SkuFeatures] = {}
        self._default = default

    def set_features(self, sku_id: str, size: str, features: SkuFeatures) -> None:
        self._data[(sku_id, size)] = features

    async def get_features(self, sku_id: str, size: str) -> SkuFeatures:
        return self._data.get((sku_id, size), self._default)
