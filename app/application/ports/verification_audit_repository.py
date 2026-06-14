# app/application/ports/verification_audit_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.verification_audit import VerificationAuditEntry


class VerificationAuditRepository(ABC):
    @abstractmethod
    async def save(self, entry: VerificationAuditEntry) -> None: ...

    @abstractmethod
    async def get_history(self, qr_token: str) -> list[VerificationAuditEntry]: ...
