# app/api/routers/buyer_match.py | 52 lines
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas.buyer_match_schemas import BuyerMatchResponse, ComputeBuyerMatchRequest
from app.application.use_cases.buyer_match_dto import BuyerMatchRequest
from app.application.use_cases.get_buyer_match_use_case import GetBuyerMatchUseCase
from app.application.use_cases.match_buyer_use_case import MatchBuyerUseCase
from app.container import Container

router = APIRouter(prefix="/buyer-match", tags=["buyer-match"])


@router.post("/compute", response_model=BuyerMatchResponse, status_code=200)
@inject
async def compute_buyer_match(
    body: ComputeBuyerMatchRequest,
    use_case: MatchBuyerUseCase = Depends(Provide[Container.match_buyer_use_case]),
) -> BuyerMatchResponse:
    result = await use_case.execute(
        BuyerMatchRequest(
            return_id=body.return_id,
            sku_id=body.sku_id,
            pincode=body.pincode,
            grade=body.grade,
        )
    )
    return BuyerMatchResponse(
        return_id=result.return_id,
        sku_id=result.sku_id,
        pincode=result.pincode,
        grade=result.grade,
        demand_score=result.demand_score,
        demand_level=result.demand_level,
        estimated_buyers=result.estimated_buyers,
        match_found=result.match_found,
        eligibility=result.eligibility,
        confidence=result.confidence,
        p2p_recommended=result.p2p_recommended,
        computed_at=result.computed_at,
    )


@router.get("/{return_id}", response_model=BuyerMatchResponse, status_code=200)
@inject
async def get_buyer_match(
    return_id: str,
    use_case: GetBuyerMatchUseCase = Depends(Provide[Container.get_buyer_match_use_case]),
) -> BuyerMatchResponse:
    result = await use_case.execute(return_id)
    return BuyerMatchResponse(
        return_id=result.return_id,
        sku_id=result.sku_id,
        pincode=result.pincode,
        grade=result.grade,
        demand_score=result.demand_score,
        demand_level=result.demand_level,
        estimated_buyers=result.estimated_buyers,
        match_found=result.match_found,
        eligibility=result.eligibility,
        confidence=result.confidence,
        p2p_recommended=result.p2p_recommended,
        computed_at=result.computed_at,
    )