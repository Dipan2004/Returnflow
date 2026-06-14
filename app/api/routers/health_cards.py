# app/api/routers/health_cards.py
from __future__ import annotations

from datetime import UTC, datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBaseModel

from app.api.schemas.health_card_schemas import (
    GenerateHealthCardResponse,
    HealthCardDetailResponse,
)
from app.application.use_cases.generate_health_card_use_case import GenerateHealthCardUseCase
from app.application.use_cases.get_health_card_by_qr_use_case import GetHealthCardByQRUseCase
from app.application.use_cases.get_health_card_use_case import GetHealthCardUseCase
from app.container import Container

router = APIRouter(prefix="/health-cards", tags=["health-cards"])


@router.post(
    "/generate/{return_id}",
    response_model=GenerateHealthCardResponse,
    status_code=201,
)
@inject
async def generate_health_card(
    return_id: str,
    use_case: GenerateHealthCardUseCase = Depends(Provide[Container.generate_health_card_use_case]),
) -> GenerateHealthCardResponse:
    result = await use_case.execute(return_id)
    return GenerateHealthCardResponse(
        return_id=result.return_id,
        qr_token=result.qr_token,
        verification_url=result.verification_url,
        route=result.route,
        condition_grade=result.condition_grade,
        recovery_value=result.recovery_value,
        created_at=result.created_at,
    )


@router.get("/{return_id}", response_model=HealthCardDetailResponse, status_code=200)
@inject
async def get_health_card(
    return_id: str,
    use_case: GetHealthCardUseCase = Depends(Provide[Container.get_health_card_use_case]),
) -> HealthCardDetailResponse:
    result = await use_case.execute(return_id)
    return HealthCardDetailResponse(
        return_id=result.return_id,
        sku_id=result.sku_id,
        grade=result.grade,
        confidence=result.confidence,
        damage_description=result.damage_description,
        route=result.route,
        mrp=result.mrp,
        recovery_value=result.recovery_value,
        value_delta=result.value_delta,
        qr_token=result.qr_token,
        verification_url=result.verification_url,
        status=result.status,
        image_keys=result.image_keys,
        created_at=result.created_at,
        fraud_risk=result.fraud_risk,
        buyer_match_used=result.buyer_match_used,
    )


@router.get(
    "/by-qr/{qr_token}",
    response_model=HealthCardDetailResponse,
    status_code=200,
)
@inject
async def get_health_card_by_qr(
    qr_token: str,
    use_case: GetHealthCardByQRUseCase = Depends(Provide[Container.get_health_card_by_qr_use_case]),
) -> HealthCardDetailResponse:
    result = await use_case.execute(qr_token)
    return HealthCardDetailResponse(
        return_id=result.return_id,
        sku_id=result.sku_id,
        grade=result.grade,
        confidence=result.confidence,
        damage_description=result.damage_description,
        route=result.route,
        mrp=result.mrp,
        recovery_value=result.recovery_value,
        value_delta=result.value_delta,
        qr_token=result.qr_token,
        verification_url=result.verification_url,
        status=result.status,
        image_keys=result.image_keys,
        created_at=result.created_at,
        fraud_risk=result.fraud_risk,
        buyer_match_used=result.buyer_match_used,
    )


class HandoffConfirmResponse(PydanticBaseModel):
    return_id: str
    confirmed: bool
    confirmed_at: datetime


@router.post(
    "/{return_id}/confirm-handoff",
    response_model=HandoffConfirmResponse,
    status_code=200,
)
async def confirm_handoff(return_id: str) -> HandoffConfirmResponse:
    return HandoffConfirmResponse(
        return_id=return_id,
        confirmed=True,
        confirmed_at=datetime.now(UTC),
    )
