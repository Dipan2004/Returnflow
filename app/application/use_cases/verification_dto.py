# app/application/use_cases/verification_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VerificationResultDTO:
    qr_token: str
    valid: bool
    status: str
    alert: str
    return_id: str | None
    scanned_by: str | None
    scanned_at: datetime | None
    previous_scan_at: datetime | None


@dataclass(frozen=True)
class VerificationAuditDTO:
    qr_token: str
    return_id: str | None
    agent_id: str
    status: str
    alert: str
    verified_at: datetime


@dataclass(frozen=True)
class VerificationHistoryDTO:
    qr_token: str
    total_scans: int
    entries: list[VerificationAuditDTO]
