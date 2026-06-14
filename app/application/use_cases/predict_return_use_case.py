# app/application/use_cases/predict_return_use_case.py
from __future__ import annotations

from app.application.ports.buyer_feature_port import BuyerFeaturePort
from app.application.ports.prediction_model_port import PredictionModelPort
from app.application.ports.sku_feature_port import SkuFeaturePort
from app.application.use_cases.prevent_iq_dto import PredictReturnRequest, PredictReturnResponse
from app.domain.services.prevent_iq_engine import (
    BuyerFeatures as DomainBuyerFeatures,
)
from app.domain.services.prevent_iq_engine import (
    PreventIQEngine,
)
from app.domain.services.prevent_iq_engine import (
    SkuFeatures as DomainSkuFeatures,
)
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class PredictReturnUseCase:
    def __init__(
        self,
        buyer_feature_port: BuyerFeaturePort,
        sku_feature_port: SkuFeaturePort,
        prediction_model: PredictionModelPort,
        prevent_iq_engine: PreventIQEngine,
    ) -> None:
        self._buyer_feature_port = buyer_feature_port
        self._sku_feature_port = sku_feature_port
        self._prediction_model = prediction_model
        self._engine = prevent_iq_engine

    async def execute(self, request: PredictReturnRequest) -> PredictReturnResponse:
        buyer_features = await self._buyer_feature_port.get_features(request.buyer_id)
        sku_features = await self._sku_feature_port.get_features(request.sku_id, request.size)

        feature_vector = [
            buyer_features.return_rate,
            sku_features.category_return_rate,
            sku_features.size_mismatch_rate,
        ]
        model_score = await self._prediction_model.predict(feature_vector)

        domain_buyer = DomainBuyerFeatures(
            buyer_id=request.buyer_id,
            return_rate=buyer_features.return_rate,
            total_returns=buyer_features.total_returns,
            avg_days_between_returns=buyer_features.avg_days_between_returns,
            category_preference=buyer_features.category_preference,
        )
        domain_sku = DomainSkuFeatures(
            sku_id=request.sku_id,
            size=request.size,
            category_return_rate=sku_features.category_return_rate,
            size_mismatch_rate=sku_features.size_mismatch_rate,
            brand=sku_features.brand,
            recommended_size=sku_features.recommended_size,
            keep_rate_for_recommended=sku_features.keep_rate_for_recommended,
        )

        prediction = self._engine.predict(domain_buyer, domain_sku, model_score)

        logger.info(
            "Return prediction computed",
            buyer_id=request.buyer_id,
            sku_id=request.sku_id,
            risk_level=prediction.risk_level,
        )

        return PredictReturnResponse(
            return_probability=prediction.return_probability.value,
            risk_level=prediction.risk_level,
            keep_rate=prediction.keep_rate.value,
            recommended_size=prediction.recommended_size,
            size_warning=prediction.size_warning,
            category_avg_return_rate=sku_features.category_return_rate,
        )
