# app/application/use_cases/get_verification_history_use_case.py
from __future__ import annotations

from app.application.ports.verification_audit_repository import VerificationAuditRepository
from app.application.use_cases.verification_dto import (
    VerificationAuditDTO,
    VerificationHistoryDTO,
)


class GetVerificationHistoryUseCase:
    def __init__(self, verification_audit_repository: VerificationAuditRepository) -> None:
        self._audit = verification_audit_repository

    async def execute(self, qr_token: str) -> VerificationHistoryDTO:
        entries = await self._audit.get_history(qr_token)
        return VerificationHistoryDTO(
            qr_token=qr_token,
            total_scans=len(entries),
            entries=[
                VerificationAuditDTO(
                    qr_token=e.qr_token,
                    return_id=e.return_id,
                    agent_id=e.agent_id,
                    status=e.status.value,
                    alert=e.alert.value,
                    verified_at=e.verified_at,
                )
                for e in entries
            ],
        )
