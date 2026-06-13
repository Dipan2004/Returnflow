from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from app.domain.exceptions import DomainValidationError, QRTokenAlreadyScannedError
from app.domain.value_objects.return_id import ReturnId


class QRToken:
    def __init__(
        self,
        token: str,
        return_id: ReturnId,
        created_at: datetime,
        ttl_hours: int,
        scanned: bool = False,
        scanned_at: datetime | None = None,
        scanned_by: str | None = None,
    ) -> None:
        if not token or len(token) < 32:
            raise DomainValidationError(
                f"QR token must be at least 32 characters, got {len(token) if token else 0}"
            )
        if ttl_hours < 1:
            raise DomainValidationError("ttl_hours must be at least 1")

        self._token = token
        self._return_id = return_id
        self._created_at = created_at
        self._ttl_hours = ttl_hours
        self._scanned = scanned
        self._scanned_at = scanned_at
        self._scanned_by = scanned_by

    @classmethod
    def generate(cls, return_id: ReturnId, ttl_hours: int = 48) -> QRToken:
        token = secrets.token_urlsafe(32)
        return cls(
            token=token,
            return_id=return_id,
            created_at=datetime.now(UTC),
            ttl_hours=ttl_hours,
        )

    def consume(self, agent_id: str) -> None:
        if self._scanned:
            raise QRTokenAlreadyScannedError(self._token)
        if self.is_expired():
            raise DomainValidationError(f"QR token '{self._token}' has expired")
        if not agent_id or not agent_id.strip():
            raise DomainValidationError("agent_id cannot be empty when consuming QR token")
        self._scanned = True
        self._scanned_at = datetime.now(UTC)
        self._scanned_by = agent_id.strip()

    def is_expired(self) -> bool:
        expiry = self._created_at + timedelta(hours=self._ttl_hours)
        return datetime.now(UTC) > expiry

    def is_valid_for_use(self) -> bool:
        return not self._scanned and not self.is_expired()

    @property
    def token(self) -> str:
        return self._token

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def ttl_hours(self) -> int:
        return self._ttl_hours

    @property
    def expires_at(self) -> datetime:
        return self._created_at + timedelta(hours=self._ttl_hours)

    @property
    def scanned(self) -> bool:
        return self._scanned

    @property
    def scanned_at(self) -> datetime | None:
        return self._scanned_at

    @property
    def scanned_by(self) -> str | None:
        return self._scanned_by

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QRToken):
            return NotImplemented
        return self._token == other._token

    def __hash__(self) -> int:
        return hash(self._token)

    def __repr__(self) -> str:
        return f"QRToken(token={self._token[:8]}..., scanned={self._scanned})"