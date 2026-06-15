# app/infrastructure/persistence/in_memory_verification_audit_repository.py
from __future__ import annotations

from app.application.ports.verification_audit_repository import VerificationAuditRepository
from app.domain.entities.verification_audit import VerificationAuditEntry
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryVerificationAuditRepository(VerificationAuditRepository):
    def __init__(self) -> None:
        STORE.setdefault("verification_audits", [])

    async def save(self, entry: VerificationAuditEntry) -> None:
        STORE["verification_audits"].append(entry)

    async def get_history(self, qr_token: str) -> list[VerificationAuditEntry]:
        return [e for e in STORE["verification_audits"] if e.qr_token == qr_token]
