# app/api/routers/dispositions.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas.disposition_schemas import (
    CalculateDispositionRequest,
    DispositionResponse,
    RecoveryBreakdownResponse,
)
from app.api.schemas.orchestration_schemas import OrchestrationResponseSchema
from app.application.use_cases.calculate_disposition_use_case import (
    CalculateDispositionUseCase,
)
from app.application.use_cases.disposition_dto import DispositionRequest
from app.application.use_cases.get_disposition_use_case import GetDispositionUseCase
from app.application.use_cases.orchestrate_disposition_use_case import (
    OrchestrateDispositionUseCase,
)
from app.container import Container

router = APIRouter(prefix="/dispositions", tags=["disposition"])


@router.post(
    "/calculate/{return_id}",
    response_model=OrchestrationResponseSchema,
    status_code=200,
)
@inject
async def orchestrate_disposition(
    return_id: str,
    use_case: OrchestrateDispositionUseCase = Depends(
        Provide[Container.orchestrate_disposition_use_case]
    ),
) -> OrchestrationResponseSchema:
    result = await use_case.execute(return_id)
    return OrchestrationResponseSchema(
        return_id=result.return_id,
        route=result.route,
        recovery_value=result.recovery_value,
        decision_reason=result.decision_reason,
        fraud_override_applied=result.fraud_override_applied,
        buyer_match_used=result.buyer_match_used,
        demand_score=result.demand_score,
        confidence=result.confidence,
        grade=result.grade,
        liquidation_baseline=result.liquidation_baseline,
        value_delta=result.value_delta,
        recovery_percentage=result.recovery_percentage,
        decided_at=result.decided_at,
    )


@router.post("/calculate", response_model=DispositionResponse, status_code=200)
@inject
async def calculate_disposition(
    body: CalculateDispositionRequest,
    use_case: CalculateDispositionUseCase = Depends(
        Provide[Container.calculate_disposition_use_case]
    ),
) -> DispositionResponse:
    result = await use_case.execute(
        DispositionRequest(
            return_id=body.return_id,
            sku_id=body.sku_id,
            seller_pincode=body.seller_pincode,
            mrp=body.mrp,
        )
    )
    return DispositionResponse(
        return_id=result.return_id,
        route=result.route,
        route_label=result.route_label,
        grade=result.grade,
        route_reason=result.route_reason,
        recovery=RecoveryBreakdownResponse(
            mrp=result.recovery.mrp,
            recovery_value=result.recovery.recovery_value,
            liquidation_baseline=result.recovery.liquidation_baseline,
            value_delta=result.recovery.value_delta,
            recovery_percentage=result.recovery.recovery_percentage,
        ),
        fraud_flagged=result.fraud_flagged,
        matched_buyer_id=result.matched_buyer_id,
        distance_km=result.distance_km,
        decided_at=result.decided_at,
    )


@router.get("/{return_id}", response_model=DispositionResponse, status_code=200)
@inject
async def get_disposition(
    return_id: str,
    use_case: GetDispositionUseCase = Depends(
        Provide[Container.get_disposition_use_case]
    ),
) -> DispositionResponse:
    result = await use_case.execute(return_id)
    return DispositionResponse(
        return_id=result.return_id,
        route=result.route,
        route_label=result.route_label,
        grade=result.grade,
        route_reason=result.route_reason,
        recovery=RecoveryBreakdownResponse(
            mrp=result.recovery.mrp,
            recovery_value=result.recovery.recovery_value,
            liquidation_baseline=result.recovery.liquidation_baseline,
            value_delta=result.recovery.value_delta,
            recovery_percentage=result.recovery.recovery_percentage,
        ),
        fraud_flagged=result.fraud_flagged,
        matched_buyer_id=result.matched_buyer_id,
        distance_km=result.distance_km,
        decided_at=result.decided_at,
    )