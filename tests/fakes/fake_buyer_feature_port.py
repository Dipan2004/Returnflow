# tests/fakes/fake_buyer_feature_port.py
from __future__ import annotations

from app.application.ports.buyer_feature_port import BuyerFeaturePort, BuyerFeatures

_DEFAULT = BuyerFeatures(
    return_rate=0.15,
    total_returns=2,
    avg_days_between_returns=30.0,
    category_preference="general",
)


class FakeBuyerFeaturePort(BuyerFeaturePort):
    def __init__(self, default: BuyerFeatures = _DEFAULT) -> None:
        self._data: dict[str, BuyerFeatures] = {}
        self._default = default

    def set_features(self, buyer_id: str, features: BuyerFeatures) -> None:
        self._data[buyer_id] = features

    async def get_features(self, buyer_id: str) -> BuyerFeatures:
        return self._data.get(buyer_id, self._default)
