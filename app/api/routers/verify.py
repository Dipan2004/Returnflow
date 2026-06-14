# app/api/routers/verify.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.api.schemas.verification_schemas import (
    VerificationAuditResponse,
    VerificationHistoryResponse,
    VerificationResponse,
)
from app.application.use_cases.get_verification_history_use_case import (
    GetVerificationHistoryUseCase,
)
from app.application.use_cases.verify_qr_token_use_case import VerifyQrTokenUseCase
from app.container import Container

router = APIRouter(prefix="/verify", tags=["verification"])


@router.get("/{qr_token}", response_model=VerificationResponse, status_code=200)
@inject
async def verify_qr_token(
    qr_token: str,
    agent_id: str = Query(..., min_length=1),
    use_case: VerifyQrTokenUseCase = Depends(Provide[Container.verify_qr_token_use_case]),
) -> VerificationResponse:
    result = await use_case.execute(qr_token, agent_id)
    return VerificationResponse(
        qr_token=result.qr_token,
        valid=result.valid,
        status=result.status,
        alert=result.alert,
        return_id=result.return_id,
        scanned_by=result.scanned_by,
        scanned_at=result.scanned_at,
        previous_scan_at=result.previous_scan_at,
    )


@router.get(
    "/{qr_token}/history",
    response_model=VerificationHistoryResponse,
    status_code=200,
)
@inject
async def get_verification_history(
    qr_token: str,
    use_case: GetVerificationHistoryUseCase = Depends(
        Provide[Container.get_verification_history_use_case]
    ),
) -> VerificationHistoryResponse:
    result = await use_case.execute(qr_token)
    return VerificationHistoryResponse(
        qr_token=result.qr_token,
        total_scans=result.total_scans,
        entries=[
            VerificationAuditResponse(
                qr_token=e.qr_token,
                return_id=e.return_id,
                agent_id=e.agent_id,
                status=e.status,
                alert=e.alert,
                verified_at=e.verified_at,
            )
            for e in result.entries
        ],
    )
