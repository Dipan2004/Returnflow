# app/application/use_cases/match_buyer_use_case.py | 66 lines
from __future__ import annotations

from app.application.ports.buyer_match_repository import BuyerMatchRepository
from app.application.ports.buyer_matching_port import BuyerMatchingPort
from app.application.ports.demand_index_port import DemandIndexPort
from app.application.use_cases.buyer_match_dto import BuyerMatchRequest, BuyerMatchResponse
from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class MatchBuyerUseCase:
    def __init__(
        self,
        demand_index_port: DemandIndexPort,
        buyer_matching_port: BuyerMatchingPort,
        buyer_match_repository: BuyerMatchRepository,
        buyer_matching_engine: BuyerMatchingEngine,
    ) -> None:
        self._demand_index = demand_index_port
        self._buyer_matching = buyer_matching_port
        self._repository = buyer_match_repository
        self._engine = buyer_matching_engine

    async def execute(self, request: BuyerMatchRequest) -> BuyerMatchResponse:
        return_id = ReturnId(request.return_id)
        grade = Grade.from_string(request.grade)

        demand_score = await self._demand_index.get_demand_score(request.sku_id)
        buyer_count = await self._buyer_matching.get_available_buyer_count(
            request.sku_id, request.pincode
        )

        result = self._engine.compute(
            return_id=return_id,
            sku_id=request.sku_id,
            pincode=request.pincode,
            grade=grade,
            raw_demand_score=demand_score,
            available_buyer_count=buyer_count,
        )

        await self._repository.save(result)

        logger.info(
            "Buyer match computed",
            return_id=request.return_id,
            match_found=result.match_found,
            p2p_recommended=result.p2p_recommended,
            confidence=result.confidence.value,
        )

        return BuyerMatchResponse(
            return_id=request.return_id,
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