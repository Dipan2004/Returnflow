# app/domain/services/prevent_iq_engine.py
from __future__ import annotations

from app.domain.entities.return_prediction import ReturnPrediction
from app.domain.entities.size_recommendation import SizeRecommendation
from app.domain.value_objects.keep_rate import KeepRate
from app.domain.value_objects.return_probability import ReturnProbability

_MISMATCH_WARNING_THRESHOLD = 0.25


class PreventIQEngine:
    def predict(
        self,
        buyer_features: BuyerFeatures,
        sku_features: SkuFeatures,
        model_score: float,
    ) -> ReturnPrediction:
        capped_score = min(model_score, 1.0)
        return_probability = ReturnProbability(capped_score)
        keep_rate = KeepRate(sku_features.keep_rate_for_recommended)

        size_warning: str | None = None
        if sku_features.size_mismatch_rate > _MISMATCH_WARNING_THRESHOLD:
            size_warning = (
                f"High size mismatch rate ({sku_features.size_mismatch_rate:.0%}) "
                f"for this SKU. Consider size {sku_features.recommended_size}."
            )

        return ReturnPrediction.create(
            buyer_id=buyer_features.buyer_id,
            sku_id=sku_features.sku_id,
            size=sku_features.size,
            return_probability=return_probability,
            keep_rate=keep_rate,
            size_warning=size_warning,
            recommended_size=sku_features.recommended_size,
        )

    def recommend_size(
        self,
        sku_id: str,
        brand: str,
        current_size: str,
        sku_features: SkuFeatures,
    ) -> SizeRecommendation:
        confidence = 1.0 - sku_features.size_mismatch_rate
        return SizeRecommendation(
            sku_id=sku_id,
            current_size=current_size,
            recommended_size=sku_features.recommended_size,
            confidence=confidence,
            mismatch_rate=sku_features.size_mismatch_rate,
            brand=brand,
        )


class BuyerFeatures:
    __slots__ = (
        "buyer_id",
        "return_rate",
        "total_returns",
        "avg_days_between_returns",
        "category_preference",
    )

    def __init__(
        self,
        buyer_id: str,
        return_rate: float,
        total_returns: int,
        avg_days_between_returns: float,
        category_preference: str,
    ) -> None:
        self.buyer_id = buyer_id
        self.return_rate = return_rate
        self.total_returns = total_returns
        self.avg_days_between_returns = avg_days_between_returns
        self.category_preference = category_preference


class SkuFeatures:
    __slots__ = (
        "sku_id",
        "size",
        "category_return_rate",
        "size_mismatch_rate",
        "brand",
        "recommended_size",
        "keep_rate_for_recommended",
    )

    def __init__(
        self,
        sku_id: str,
        size: str,
        category_return_rate: float,
        size_mismatch_rate: float,
        brand: str,
        recommended_size: str,
        keep_rate_for_recommended: float,
    ) -> None:
        self.sku_id = sku_id
        self.size = size
        self.category_return_rate = category_return_rate
        self.size_mismatch_rate = size_mismatch_rate
        self.brand = brand
        self.recommended_size = recommended_size
        self.keep_rate_for_recommended = keep_rate_for_recommended
