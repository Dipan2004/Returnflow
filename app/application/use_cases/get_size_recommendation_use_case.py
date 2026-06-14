# app/application/use_cases/get_size_recommendation_use_case.py
from __future__ import annotations

from app.application.ports.sku_feature_port import SkuFeaturePort
from app.application.use_cases.prevent_iq_dto import SizeRecommendationResponse
from app.domain.services.prevent_iq_engine import PreventIQEngine
from app.domain.services.prevent_iq_engine import SkuFeatures as DomainSkuFeatures
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GetSizeRecommendationUseCase:
    def __init__(
        self,
        sku_feature_port: SkuFeaturePort,
        prevent_iq_engine: PreventIQEngine,
    ) -> None:
        self._sku_feature_port = sku_feature_port
        self._engine = prevent_iq_engine

    async def execute(
        self, sku_id: str, size: str, brand: str | None = None
    ) -> SizeRecommendationResponse:
        sku_features = await self._sku_feature_port.get_features(sku_id, size)

        resolved_brand = brand if brand else sku_features.brand

        domain_sku = DomainSkuFeatures(
            sku_id=sku_id,
            size=size,
            category_return_rate=sku_features.category_return_rate,
            size_mismatch_rate=sku_features.size_mismatch_rate,
            brand=sku_features.brand,
            recommended_size=sku_features.recommended_size,
            keep_rate_for_recommended=sku_features.keep_rate_for_recommended,
        )

        recommendation = self._engine.recommend_size(
            sku_id=sku_id,
            brand=resolved_brand,
            current_size=size,
            sku_features=domain_sku,
        )

        logger.info(
            "Size recommendation computed",
            sku_id=sku_id,
            recommended_size=recommendation.recommended_size,
            confidence=recommendation.confidence,
        )

        return SizeRecommendationResponse(
            recommended_size=recommendation.recommended_size,
            confidence=recommendation.confidence,
            current_size=recommendation.current_size,
            mismatch_rate=recommendation.mismatch_rate,
        )
