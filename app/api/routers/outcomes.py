# app/api/routers/outcomes.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas.outcome_schemas import OutcomeResponseSchema, RejectRequest
from app.application.use_cases.accept_buyer_match_use_case import AcceptBuyerMatchUseCase
from app.application.use_cases.get_outcome_use_case import GetOutcomeUseCase
from app.application.use_cases.reject_buyer_match_use_case import RejectBuyerMatchUseCase
from app.container import Container

router = APIRouter(tags=["outcomes"])


@router.post(
    "/buyers/{buyer_id}/accept/{return_id}",
    response_model=OutcomeResponseSchema,
    status_code=200,
)
@inject
async def accept_buyer_match(
    buyer_id: str,
    return_id: str,
    use_case: AcceptBuyerMatchUseCase = Depends(
        Provide[Container.accept_buyer_match_use_case]
    ),
) -> OutcomeResponseSchema:
    result = await use_case.execute(buyer_id, return_id)
    return OutcomeResponseSchema(
        return_id=result.return_id,
        buyer_id=result.buyer_id,
        route=result.route,
        status=result.status,
        recovery_value=result.recovery_value,
        fraud_flag=result.fraud_flag,
        outcome_reason=result.outcome_reason,
        created_at=result.created_at,
        resolved_at=result.resolved_at,
    )


@router.post(
    "/buyers/{buyer_id}/reject/{return_id}",
    response_model=OutcomeResponseSchema,
    status_code=200,
)
@inject
async def reject_buyer_match(
    buyer_id: str,
    return_id: str,
    body: RejectRequest,
    use_case: RejectBuyerMatchUseCase = Depends(
        Provide[Container.reject_buyer_match_use_case]
    ),
) -> OutcomeResponseSchema:
    result = await use_case.execute(buyer_id, return_id, body.reason)
    return OutcomeResponseSchema(
        return_id=result.return_id,
        buyer_id=result.buyer_id,
        route=result.route,
        status=result.status,
        recovery_value=result.recovery_value,
        fraud_flag=result.fraud_flag,
        outcome_reason=result.outcome_reason,
        created_at=result.created_at,
        resolved_at=result.resolved_at,
    )


@router.get(
    "/outcomes/{return_id}",
    response_model=OutcomeResponseSchema,
    status_code=200,
)
@inject
async def get_outcome(
    return_id: str,
    use_case: GetOutcomeUseCase = Depends(Provide[Container.get_outcome_use_case]),
) -> OutcomeResponseSchema:
    result = await use_case.execute(return_id)
    return OutcomeResponseSchema(
        return_id=result.return_id,
        buyer_id=result.buyer_id,
        route=result.route,
        status=result.status,
        recovery_value=result.recovery_value,
        fraud_flag=result.fraud_flag,
        outcome_reason=result.outcome_reason,
        created_at=result.created_at,
        resolved_at=result.resolved_at,
    )
