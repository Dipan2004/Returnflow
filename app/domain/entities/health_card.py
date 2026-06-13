from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from app.domain.exceptions import DomainValidationError, InvalidStateTransitionError
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route


class HealthCardStatus(StrEnum):
    PENDING_BUYER_ACCEPT = "PENDING_BUYER_ACCEPT"
    ACCEPTED = "ACCEPTED"
    DISPUTED = "DISPUTED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


_VALID_HEALTH_CARD_TRANSITIONS: dict[HealthCardStatus, set[HealthCardStatus]] = {
    HealthCardStatus.PENDING_BUYER_ACCEPT: {
        HealthCardStatus.ACCEPTED,
        HealthCardStatus.DISPUTED,
        HealthCardStatus.EXPIRED,
    },
    HealthCardStatus.ACCEPTED: {HealthCardStatus.COMPLETED, HealthCardStatus.DISPUTED},
    HealthCardStatus.DISPUTED: {HealthCardStatus.COMPLETED},
    HealthCardStatus.COMPLETED: set(),
    HealthCardStatus.EXPIRED: set(),
}


class HealthCard:
    def __init__(
        self,
        return_id: ReturnId,
        sku_id: str,
        grade: Grade,
        confidence: ConfidenceScore,
        damage_description: str,
        route: Route,
        mrp: Money,
        recovery_value: Money,
        value_delta: Money,
        image_keys: list[ImageKey],
        qr_token: str,
        qr_url: str,
        created_at: datetime,
        ttl_hours: int,
        status: HealthCardStatus = HealthCardStatus.PENDING_BUYER_ACCEPT,
        dispute_reason: str | None = None,
        accepted_at: datetime | None = None,
        disputed_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None:
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty on HealthCard")
        if not qr_token or not qr_token.strip():
            raise DomainValidationError("qr_token cannot be empty")
        if not qr_url or not qr_url.strip():
            raise DomainValidationError("qr_url cannot be empty")
        if not image_keys:
            raise DomainValidationError("HealthCard must have at least one image_key")
        if ttl_hours < 1:
            raise DomainValidationError("ttl_hours must be at least 1")

        self._return_id = return_id
        self._sku_id = sku_id.strip()
        self._grade = grade
        self._confidence = confidence
        self._damage_description = damage_description.strip()
        self._route = route
        self._mrp = mrp
        self._recovery_value = recovery_value
        self._value_delta = value_delta
        self._image_keys = image_keys
        self._qr_token = qr_token.strip()
        self._qr_url = qr_url.strip()
        self._created_at = created_at
        self._ttl_hours = ttl_hours
        self._status = status
        self._dispute_reason = dispute_reason
        self._accepted_at = accepted_at
        self._disputed_at = disputed_at
        self._completed_at = completed_at

    def _transition(self, new_status: HealthCardStatus) -> None:
        allowed = _VALID_HEALTH_CARD_TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                entity="HealthCard",
                current=self._status.value,
                attempted=new_status.value,
            )
        self._status = new_status

    def accept(self) -> None:
        self._transition(HealthCardStatus.ACCEPTED)
        self._accepted_at = datetime.now(UTC)

    def dispute(self, reason: str) -> None:
        if not reason or not reason.strip():
            raise DomainValidationError("Dispute reason cannot be empty")
        self._transition(HealthCardStatus.DISPUTED)
        self._dispute_reason = reason.strip()
        self._disputed_at = datetime.now(UTC)

    def complete(self) -> None:
        self._transition(HealthCardStatus.COMPLETED)
        self._completed_at = datetime.now(UTC)

    def expire(self) -> None:
        self._transition(HealthCardStatus.EXPIRED)

    def is_expired(self) -> bool:
        from datetime import timedelta
        expiry = self._created_at + timedelta(hours=self._ttl_hours)
        return datetime.now(UTC) > expiry

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def grade(self) -> Grade:
        return self._grade

    @property
    def confidence(self) -> ConfidenceScore:
        return self._confidence

    @property
    def damage_description(self) -> str:
        return self._damage_description

    @property
    def route(self) -> Route:
        return self._route

    @property
    def mrp(self) -> Money:
        return self._mrp

    @property
    def recovery_value(self) -> Money:
        return self._recovery_value

    @property
    def value_delta(self) -> Money:
        return self._value_delta

    @property
    def image_keys(self) -> list[ImageKey]:
        return list(self._image_keys)

    @property
    def qr_token(self) -> str:
        return self._qr_token

    @property
    def qr_url(self) -> str:
        return self._qr_url

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def ttl_hours(self) -> int:
        return self._ttl_hours

    @property
    def status(self) -> HealthCardStatus:
        return self._status

    @property
    def dispute_reason(self) -> str | None:
        return self._dispute_reason

    @property
    def accepted_at(self) -> datetime | None:
        return self._accepted_at

    @property
    def disputed_at(self) -> datetime | None:
        return self._disputed_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HealthCard):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)

    def __repr__(self) -> str:
        return (
            f"HealthCard(return_id={self._return_id}, grade={self._grade.value}, "
            f"route={self._route.value}, status={self._status.value})"
        )