# app/api/routers/predict.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.api.schemas.prediction_schemas import PredictReturnResponse, SizeRecommendationResponse
from app.application.use_cases.get_size_recommendation_use_case import (
    GetSizeRecommendationUseCase,
)
from app.application.use_cases.predict_return_use_case import PredictReturnUseCase
from app.application.use_cases.prevent_iq_dto import PredictReturnRequest
from app.container import Container

router = APIRouter(prefix="/prevent-iq", tags=["prevent-iq"])


@router.get("/predict-return", response_model=PredictReturnResponse, status_code=200)
@inject
async def predict_return(
    buyer_id: str = Query(min_length=1),
    sku_id: str = Query(min_length=1),
    size: str = Query(min_length=1),
    brand: str | None = Query(default=None),
    use_case: PredictReturnUseCase = Depends(Provide[Container.predict_return_use_case]),
) -> PredictReturnResponse:
    result = await use_case.execute(
        PredictReturnRequest(buyer_id=buyer_id, sku_id=sku_id, size=size, brand=brand)
    )
    return PredictReturnResponse(
        return_probability=result.return_probability,
        risk_level=result.risk_level,
        keep_rate=result.keep_rate,
        recommended_size=result.recommended_size,
        size_warning=result.size_warning,
        category_avg_return_rate=result.category_avg_return_rate,
    )


@router.get(
    "/size-recommendation", response_model=SizeRecommendationResponse, status_code=200
)
@inject
async def size_recommendation(
    sku_id: str = Query(min_length=1),
    size: str = Query(min_length=1),
    brand: str | None = Query(default=None),
    use_case: GetSizeRecommendationUseCase = Depends(
        Provide[Container.get_size_recommendation_use_case]
    ),
) -> SizeRecommendationResponse:
    result = await use_case.execute(sku_id=sku_id, size=size, brand=brand)
    return SizeRecommendationResponse(
        recommended_size=result.recommended_size,
        confidence=result.confidence,
        current_size=result.current_size,
        mismatch_rate=result.mismatch_rate,
    )
