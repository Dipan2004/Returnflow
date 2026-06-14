# app/domain/entities/disposition_outcome.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


class OutcomeStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DISPUTED = "DISPUTED"
    EXPIRED = "EXPIRED"


class DispositionOutcome:
    def __init__(
        self,
        return_id: ReturnId,
        buyer_id: str,
        route: str,
        status: OutcomeStatus,
        recovery_value: Decimal,
        fraud_flag: bool,
        outcome_reason: str,
        created_at: datetime,
        resolved_at: datetime | None = None,
    ) -> None:
        if not buyer_id or not buyer_id.strip():
            raise DomainValidationError("buyer_id cannot be empty")
        if recovery_value < Decimal("0"):
            raise DomainValidationError("recovery_value cannot be negative")
        self._return_id = return_id
        self._buyer_id = buyer_id.strip()
        self._route = route
        self._status = status
        self._recovery_value = recovery_value
        self._fraud_flag = fraud_flag
        self._outcome_reason = outcome_reason.strip()
        self._created_at = created_at
        self._resolved_at = resolved_at

    @classmethod
    def create_pending(
        cls,
        return_id: ReturnId,
        buyer_id: str,
        route: str,
        recovery_value: Decimal,
        fraud_flag: bool = False,
    ) -> DispositionOutcome:
        return cls(
            return_id=return_id,
            buyer_id=buyer_id,
            route=route,
            status=OutcomeStatus.PENDING,
            recovery_value=recovery_value,
            fraud_flag=fraud_flag,
            outcome_reason="Awaiting buyer decision",
            created_at=datetime.now(UTC),
        )

    def accept(self) -> None:
        if self._status != OutcomeStatus.PENDING:
            raise DomainValidationError(
                f"Cannot accept outcome in status {self._status.value}"
            )
        self._status = OutcomeStatus.ACCEPTED
        self._outcome_reason = "Buyer accepted the offer"
        self._resolved_at = datetime.now(UTC)

    def reject(self, reason: str) -> None:
        if self._status != OutcomeStatus.PENDING:
            raise DomainValidationError(
                f"Cannot reject outcome in status {self._status.value}"
            )
        if not reason or not reason.strip():
            raise DomainValidationError("Rejection reason cannot be empty")
        self._status = OutcomeStatus.REJECTED
        self._outcome_reason = reason.strip()
        self._resolved_at = datetime.now(UTC)

    def dispute(self, reason: str) -> None:
        if self._status not in (OutcomeStatus.PENDING, OutcomeStatus.ACCEPTED):
            raise DomainValidationError(
                f"Cannot dispute outcome in status {self._status.value}"
            )
        if not reason or not reason.strip():
            raise DomainValidationError("Dispute reason cannot be empty")
        self._status = OutcomeStatus.DISPUTED
        self._outcome_reason = reason.strip()
        self._resolved_at = datetime.now(UTC)

    def expire(self) -> None:
        if self._status != OutcomeStatus.PENDING:
            raise DomainValidationError(
                f"Cannot expire outcome in status {self._status.value}"
            )
        self._status = OutcomeStatus.EXPIRED
        self._outcome_reason = "Offer expired without buyer response"
        self._resolved_at = datetime.now(UTC)

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def buyer_id(self) -> str:
        return self._buyer_id

    @property
    def route(self) -> str:
        return self._route

    @property
    def status(self) -> OutcomeStatus:
        return self._status

    @property
    def recovery_value(self) -> Decimal:
        return self._recovery_value

    @property
    def fraud_flag(self) -> bool:
        return self._fraud_flag

    @property
    def outcome_reason(self) -> str:
        return self._outcome_reason

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def resolved_at(self) -> datetime | None:
        return self._resolved_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DispositionOutcome):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)
