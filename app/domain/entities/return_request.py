from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from app.domain.exceptions import DomainValidationError, InvalidStateTransitionError
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId


class ReturnStatus(str, Enum):
    AWAITING_IMAGES = "AWAITING_IMAGES"
    IMAGES_RECEIVED = "IMAGES_RECEIVED"
    GRADING = "GRADING"
    GRADED = "GRADED"
    ROUTED = "ROUTED"
    HEALTH_CARD_GENERATED = "HEALTH_CARD_GENERATED"
    PENDING_BUYER_ACCEPT = "PENDING_BUYER_ACCEPT"
    ACCEPTED = "ACCEPTED"
    DISPUTED = "DISPUTED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


_VALID_TRANSITIONS: dict[ReturnStatus, set[ReturnStatus]] = {
    ReturnStatus.AWAITING_IMAGES: {ReturnStatus.IMAGES_RECEIVED, ReturnStatus.CANCELLED},
    ReturnStatus.IMAGES_RECEIVED: {ReturnStatus.GRADING, ReturnStatus.CANCELLED},
    ReturnStatus.GRADING: {ReturnStatus.GRADED, ReturnStatus.HUMAN_REVIEW, ReturnStatus.CANCELLED},
    ReturnStatus.GRADED: {ReturnStatus.ROUTED},
    ReturnStatus.ROUTED: {ReturnStatus.HEALTH_CARD_GENERATED},
    ReturnStatus.HEALTH_CARD_GENERATED: {ReturnStatus.PENDING_BUYER_ACCEPT},
    ReturnStatus.PENDING_BUYER_ACCEPT: {ReturnStatus.ACCEPTED, ReturnStatus.DISPUTED},
    ReturnStatus.ACCEPTED: {ReturnStatus.COMPLETED},
    ReturnStatus.DISPUTED: {ReturnStatus.HUMAN_REVIEW},
    ReturnStatus.HUMAN_REVIEW: {ReturnStatus.GRADING, ReturnStatus.CANCELLED},
    ReturnStatus.COMPLETED: set(),
    ReturnStatus.CANCELLED: set(),
}


class ReturnRequest:
    def __init__(
        self,
        return_id: ReturnId,
        sku_id: str,
        seller_id: str,
        buyer_id: str,
        expected_image_count: int,
        created_at: datetime,
        status: ReturnStatus = ReturnStatus.AWAITING_IMAGES,
        image_keys: list[ImageKey] | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if not seller_id or not seller_id.strip():
            raise DomainValidationError("seller_id cannot be empty")
        if not buyer_id or not buyer_id.strip():
            raise DomainValidationError("buyer_id cannot be empty")
        if expected_image_count < 1 or expected_image_count > 10:
            raise DomainValidationError(
                f"expected_image_count must be between 1 and 10, got {expected_image_count}"
            )

        self._return_id = return_id
        self._sku_id = sku_id.strip()
        self._seller_id = seller_id.strip()
        self._buyer_id = buyer_id.strip()
        self._expected_image_count = expected_image_count
        self._status = status
        self._image_keys: list[ImageKey] = image_keys or []
        self._created_at = created_at
        self._updated_at = updated_at or created_at

    @classmethod
    def create(
        cls,
        sku_id: str,
        seller_id: str,
        buyer_id: str,
        expected_image_count: int = 3,
    ) -> ReturnRequest:
        now = datetime.now(timezone.utc)
        return cls(
            return_id=ReturnId.generate(),
            sku_id=sku_id,
            seller_id=seller_id,
            buyer_id=buyer_id,
            expected_image_count=expected_image_count,
            created_at=now,
        )

    def transition_to(self, new_status: ReturnStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                entity="ReturnRequest",
                current=self._status.value,
                attempted=new_status.value,
            )
        self._status = new_status
        self._updated_at = datetime.now(timezone.utc)

    def add_image_key(self, key: ImageKey) -> None:
        if self._status != ReturnStatus.AWAITING_IMAGES:
            raise InvalidStateTransitionError(
                entity="ReturnRequest",
                current=self._status.value,
                attempted="ADD_IMAGE",
            )
        if key in self._image_keys:
            return
        self._image_keys.append(key)
        if len(self._image_keys) >= self._expected_image_count:
            self.transition_to(ReturnStatus.IMAGES_RECEIVED)

    def mark_grading_started(self) -> None:
        self.transition_to(ReturnStatus.GRADING)

    def mark_graded(self) -> None:
        self.transition_to(ReturnStatus.GRADED)

    def mark_routed(self) -> None:
        self.transition_to(ReturnStatus.ROUTED)

    def mark_health_card_generated(self) -> None:
        self.transition_to(ReturnStatus.HEALTH_CARD_GENERATED)

    def mark_pending_buyer_accept(self) -> None:
        self.transition_to(ReturnStatus.PENDING_BUYER_ACCEPT)

    def mark_accepted(self) -> None:
        self.transition_to(ReturnStatus.ACCEPTED)

    def mark_disputed(self) -> None:
        self.transition_to(ReturnStatus.DISPUTED)

    def mark_human_review(self) -> None:
        self.transition_to(ReturnStatus.HUMAN_REVIEW)

    def mark_completed(self) -> None:
        self.transition_to(ReturnStatus.COMPLETED)

    def cancel(self) -> None:
        self.transition_to(ReturnStatus.CANCELLED)

    def all_images_received(self) -> bool:
        return len(self._image_keys) >= self._expected_image_count

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def seller_id(self) -> str:
        return self._seller_id

    @property
    def buyer_id(self) -> str:
        return self._buyer_id

    @property
    def expected_image_count(self) -> int:
        return self._expected_image_count

    @property
    def status(self) -> ReturnStatus:
        return self._status

    @property
    def image_keys(self) -> list[ImageKey]:
        return list(self._image_keys)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReturnRequest):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)

    def __repr__(self) -> str:
        return (
            f"ReturnRequest(id={self._return_id}, sku={self._sku_id}, "
            f"status={self._status.value})"
        )