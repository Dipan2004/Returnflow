# app/domain/entities/human_review_request.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.entities.condition_grade import DamageLabel
from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId


class ReviewStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ReviewPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


_PRIORITY_THRESHOLDS: list[tuple[float, ReviewPriority]] = [
    (40.0, ReviewPriority.CRITICAL),
    (60.0, ReviewPriority.HIGH),
    (75.0, ReviewPriority.MEDIUM),
]


def _determine_priority(confidence: float) -> ReviewPriority:
    for threshold, priority in _PRIORITY_THRESHOLDS:
        if confidence < threshold:
            return priority
    return ReviewPriority.LOW


@dataclass(frozen=True)
class HumanReviewRequest:
    return_id: ReturnId
    confidence: float
    threshold: float
    damage_labels: list[DamageLabel]
    image_keys: list[ImageKey]
    reason: str
    priority: ReviewPriority
    status: ReviewStatus
    requested_at: datetime
    reviewer_id: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None

    @classmethod
    def create(
        cls,
        return_id: ReturnId,
        confidence: float,
        threshold: float,
        damage_labels: list[DamageLabel],
        image_keys: list[ImageKey],
        reason: str,
    ) -> HumanReviewRequest:
        if not reason or not reason.strip():
            raise DomainValidationError("Human review reason cannot be empty")
        if confidence >= threshold:
            raise DomainValidationError(
                f"Confidence {confidence:.1f}% meets threshold {threshold:.1f}% — "
                f"human review not required"
            )
        return cls(
            return_id=return_id,
            confidence=confidence,
            threshold=threshold,
            damage_labels=list(damage_labels),
            image_keys=list(image_keys),
            reason=reason.strip(),
            priority=_determine_priority(confidence),
            status=ReviewStatus.PENDING,
            requested_at=datetime.now(UTC),
        )

    def to_queue_payload(self) -> dict[str, object]:
        return {
            "return_id": self.return_id.value,
            "confidence": self.confidence,
            "threshold": self.threshold,
            "damage_labels": [
                {"name": d.name, "confidence": d.confidence}
                for d in self.damage_labels
            ],
            "image_keys": [k.value for k in self.image_keys],
            "reason": self.reason,
            "priority": self.priority.value,
            "status": self.status.value,
            "requested_at": self.requested_at.isoformat(),
        }
