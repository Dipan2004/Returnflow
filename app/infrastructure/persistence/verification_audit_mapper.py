# app/infrastructure/persistence/verification_audit_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.verification_audit import VerificationAuditEntry
from app.domain.entities.verification_result import TamperAlert, VerificationStatus

ENTITY_TYPE_VERIFICATION_AUDIT = "VERIFICATION_AUDIT"


def audit_pk(qr_token: str) -> str:
    return f"QR#{qr_token}"


def audit_sk(verified_at: datetime) -> str:
    return f"AUDIT#{verified_at.isoformat()}"


def to_item(entry: VerificationAuditEntry) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": audit_pk(entry.qr_token),
        "SK": audit_sk(entry.verified_at),
        "entity_type": ENTITY_TYPE_VERIFICATION_AUDIT,
        "qr_token": entry.qr_token,
        "agent_id": entry.agent_id,
        "status": entry.status.value,
        "alert": entry.alert.value,
        "verified_at": entry.verified_at.isoformat(),
    }
    if entry.return_id:
        item["return_id"] = entry.return_id
    return item


def from_item(item: dict[str, Any]) -> VerificationAuditEntry:
    return VerificationAuditEntry(
        qr_token=item["qr_token"],
        return_id=item.get("return_id"),
        agent_id=item["agent_id"],
        status=VerificationStatus(item["status"]),
        alert=TamperAlert(item["alert"]),
        verified_at=datetime.fromisoformat(item["verified_at"]).replace(tzinfo=UTC),
    )
