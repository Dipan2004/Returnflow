# app/api/routers/fraud.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas.fraud_schemas import (
    AssessFraudRequest,
    FraudAssessmentResponse,
    FraudOverrideResponse,
    FraudSignalResponse,
)
from app.application.use_cases.assess_fraud_use_case import AssessFraudUseCase
from app.application.use_cases.fraud_dto import FraudAssessmentRequest
from app.application.use_cases.get_fraud_assessment_use_case import GetFraudAssessmentUseCase
from app.container import Container

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.post("/assess", response_model=FraudAssessmentResponse, status_code=200)
@inject
async def assess_fraud(
    body: AssessFraudRequest,
    use_case: AssessFraudUseCase = Depends(Provide[Container.assess_fraud_use_case]),
) -> FraudAssessmentResponse:
    result = await use_case.execute(
        FraudAssessmentRequest(
            return_id=body.return_id,
            buyer_id=body.buyer_id,
            sku_id=body.sku_id,
            original_route=body.original_route,
        )
    )
    override_resp: FraudOverrideResponse | None = None
    if result.override:
        override_resp = FraudOverrideResponse(
            original_route=result.override.original_route,
            overridden_route=result.override.overridden_route,
            risk_level=result.override.risk_level,
            risk_score=result.override.risk_score,
            reason=result.override.reason,
        )
    return FraudAssessmentResponse(
        return_id=result.return_id,
        buyer_id=result.buyer_id,
        sku_id=result.sku_id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        signals=[
            FraudSignalResponse(
                name=s.name, weight=s.weight, triggered=s.triggered, detail=s.detail
            )
            for s in result.signals
        ],
        override=override_resp,
        assessed_at=result.assessed_at,
    )


@router.get("/{return_id}", response_model=FraudAssessmentResponse, status_code=200)
@inject
async def get_fraud_assessment(
    return_id: str,
    use_case: GetFraudAssessmentUseCase = Depends(
        Provide[Container.get_fraud_assessment_use_case]
    ),
) -> FraudAssessmentResponse:
    result = await use_case.execute(return_id)
    override_resp: FraudOverrideResponse | None = None
    if result.override:
        override_resp = FraudOverrideResponse(
            original_route=result.override.original_route,
            overridden_route=result.override.overridden_route,
            risk_level=result.override.risk_level,
            risk_score=result.override.risk_score,
            reason=result.override.reason,
        )
    return FraudAssessmentResponse(
        return_id=result.return_id,
        buyer_id=result.buyer_id,
        sku_id=result.sku_id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        signals=[
            FraudSignalResponse(
                name=s.name, weight=s.weight, triggered=s.triggered, detail=s.detail
            )
            for s in result.signals
        ],
        override=override_resp,
        assessed_at=result.assessed_at,
    )
