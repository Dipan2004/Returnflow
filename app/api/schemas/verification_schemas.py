# app/api/schemas/verification_schemas.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class VerificationResponse(BaseModel):
    qr_token: str
    valid: bool
    status: str
    alert: str
    return_id: str | None = None
    scanned_by: str | None = None
    scanned_at: datetime | None = None
    previous_scan_at: datetime | None = None


class VerificationAuditResponse(BaseModel):
    qr_token: str
    return_id: str | None = None
    agent_id: str
    status: str
    alert: str
    verified_at: datetime


class VerificationHistoryResponse(BaseModel):
    qr_token: str
    total_scans: int
    entries: list[VerificationAuditResponse]
