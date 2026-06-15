# app/infrastructure/persistence/in_memory_verification_audit_repository.py
from __future__ import annotations

from app.application.ports.verification_audit_repository import VerificationAuditRepository
from app.domain.entities.verification_audit import VerificationAuditEntry

_AUDIT_LOG: list[VerificationAuditEntry] = []


class InMemoryVerificationAuditRepository(VerificationAuditRepository):
    def __init__(self) -> None:
        pass

    async def save(self, entry: VerificationAuditEntry) -> None:
        _AUDIT_LOG.append(entry)

    async def get_history(self, qr_token: str) -> list[VerificationAuditEntry]:
        return [e for e in _AUDIT_LOG if e.qr_token == qr_token]
