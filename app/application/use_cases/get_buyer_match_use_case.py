# app/application/use_cases/get_buyer_match_use_case.py | 42 lines
from __future__ import annotations

from app.application.ports.buyer_match_repository import BuyerMatchRepository
from app.application.use_cases.buyer_match_dto import BuyerMatchResponse
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetBuyerMatchUseCase:
    def __init__(self, buyer_match_repository: BuyerMatchRepository) -> None:
        self._repository = buyer_match_repository

    async def execute(self, return_id: str) -> BuyerMatchResponse:
        rid = ReturnId(return_id)
        result = await self._repository.get_by_return_id(rid)
        if result is None:
            raise EntityNotFoundError("BuyerMatchResult", return_id)

        return BuyerMatchResponse(
            return_id=return_id,
            sku_id=result.sku_id,
            pincode=result.pincode,
            grade=result.grade.value,
            demand_score=result.demand_score.value,
            demand_level=result.demand_level.value,
            estimated_buyers=result.estimated_buyers,
            match_found=result.match_found,
            eligibility=result.eligibility.value,
            confidence=result.confidence.value,
            p2p_recommended=result.p2p_recommended,
            computed_at=result.computed_at,
        )