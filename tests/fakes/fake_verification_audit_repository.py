# tests/fakes/fake_verification_audit_repository.py
from __future__ import annotations

from app.application.ports.verification_audit_repository import VerificationAuditRepository
from app.domain.entities.verification_audit import VerificationAuditEntry


class FakeVerificationAuditRepository(VerificationAuditRepository):
    def __init__(self) -> None:
        self._store: list[VerificationAuditEntry] = []

    async def save(self, entry: VerificationAuditEntry) -> None:
        self._store.append(entry)

    async def get_history(self, qr_token: str) -> list[VerificationAuditEntry]:
        return [e for e in self._store if e.qr_token == qr_token]

    def count(self) -> int:
        return len(self._store)
