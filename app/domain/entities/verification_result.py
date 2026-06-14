# app/domain/entities/verification_result.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class VerificationStatus(StrEnum):
    VALID = "VALID"
    ALREADY_SCANNED = "ALREADY_SCANNED"
    EXPIRED = "EXPIRED"
    NOT_FOUND = "NOT_FOUND"


class TamperAlert(StrEnum):
    NONE = "NONE"
    POSSIBLE_TAMPERING = "POSSIBLE_TAMPERING"


@dataclass(frozen=True)
class VerificationResult:
    qr_token: str
    status: VerificationStatus
    alert: TamperAlert
    return_id: str | None
    scanned_by: str | None
    scanned_at: datetime | None
    previous_scan_at: datetime | None

    @classmethod
    def valid(cls, qr_token: str, return_id: str, agent_id: str) -> VerificationResult:
        return cls(
            qr_token=qr_token,
            status=VerificationStatus.VALID,
            alert=TamperAlert.NONE,
            return_id=return_id,
            scanned_by=agent_id,
            scanned_at=datetime.now(UTC),
            previous_scan_at=None,
        )

    @classmethod
    def already_scanned(
        cls, qr_token: str, return_id: str, previous_scan_at: datetime | None
    ) -> VerificationResult:
        return cls(
            qr_token=qr_token,
            status=VerificationStatus.ALREADY_SCANNED,
            alert=TamperAlert.POSSIBLE_TAMPERING,
            return_id=return_id,
            scanned_by=None,
            scanned_at=None,
            previous_scan_at=previous_scan_at,
        )

    @classmethod
    def expired(cls, qr_token: str, return_id: str) -> VerificationResult:
        return cls(
            qr_token=qr_token,
            status=VerificationStatus.EXPIRED,
            alert=TamperAlert.NONE,
            return_id=return_id,
            scanned_by=None,
            scanned_at=None,
            previous_scan_at=None,
        )

    @classmethod
    def not_found(cls, qr_token: str) -> VerificationResult:
        return cls(
            qr_token=qr_token,
            status=VerificationStatus.NOT_FOUND,
            alert=TamperAlert.NONE,
            return_id=None,
            scanned_by=None,
            scanned_at=None,
            previous_scan_at=None,
        )
