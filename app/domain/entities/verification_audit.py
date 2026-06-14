# app/domain/entities/verification_audit.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.entities.verification_result import TamperAlert, VerificationStatus


@dataclass(frozen=True)
class VerificationAuditEntry:
    qr_token: str
    return_id: str | None
    agent_id: str
    status: VerificationStatus
    alert: TamperAlert
    verified_at: datetime

    @classmethod
    def create(
        cls,
        qr_token: str,
        return_id: str | None,
        agent_id: str,
        status: VerificationStatus,
        alert: TamperAlert,
    ) -> VerificationAuditEntry:
        return cls(
            qr_token=qr_token,
            return_id=return_id,
            agent_id=agent_id,
            status=status,
            alert=alert,
            verified_at=datetime.now(UTC),
        )
