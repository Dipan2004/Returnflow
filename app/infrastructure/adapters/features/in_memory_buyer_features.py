# app/infrastructure/adapters/features/in_memory_buyer_features.py
from __future__ import annotations

from app.application.ports.buyer_feature_port import BuyerFeaturePort, BuyerFeatures

_DEMO_DATA: dict[str, BuyerFeatures] = {
    "BUYER001": BuyerFeatures(
        return_rate=0.12,
        total_returns=3,
        avg_days_between_returns=45.0,
        category_preference="electronics",
    ),
    "BUYER002": BuyerFeatures(
        return_rate=0.45,
        total_returns=15,
        avg_days_between_returns=10.0,
        category_preference="apparel",
    ),
    "BUYER003": BuyerFeatures(
        return_rate=0.05,
        total_returns=1,
        avg_days_between_returns=90.0,
        category_preference="home",
    ),
}

_DEFAULT = BuyerFeatures(
    return_rate=0.15,
    total_returns=2,
    avg_days_between_returns=30.0,
    category_preference="general",
)


class InMemoryBuyerFeatures(BuyerFeaturePort):
    async def get_features(self, buyer_id: str) -> BuyerFeatures:
        return _DEMO_DATA.get(buyer_id, _DEFAULT)
