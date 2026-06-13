from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId


@dataclass(frozen=True)
class DamageLabel:
    name: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            from app.domain.exceptions import DomainValidationError

            raise DomainValidationError("DamageLabel name cannot be empty")
        if not 0.0 <= self.confidence <= 100.0:
            from app.domain.exceptions import DomainValidationError

            raise DomainValidationError(
                f"DamageLabel confidence must be 0-100, got {self.confidence}"
            )


class ConditionGrade:
    def __init__(
        self,
        return_id: ReturnId,
        grade: Grade,
        confidence: ConfidenceScore,
        damage_labels: list[DamageLabel],
        damage_description: str,
        image_keys: list[ImageKey],
        graded_at: datetime,
        routed_to_human_review: bool = False,
    ) -> None:
        self._return_id = return_id
        self._grade = grade
        self._confidence = confidence
        self._damage_labels = damage_labels
        self._damage_description = damage_description.strip()
        self._image_keys = image_keys
        self._graded_at = graded_at
        self._routed_to_human_review = routed_to_human_review

    @classmethod
    def create(
        cls,
        return_id: ReturnId,
        grade: Grade,
        confidence: float,
        damage_labels: list[DamageLabel],
        damage_description: str,
        image_keys: list[ImageKey],
    ) -> ConditionGrade:
        return cls(
            return_id=return_id,
            grade=grade,
            confidence=ConfidenceScore.of(confidence),
            damage_labels=damage_labels,
            damage_description=damage_description,
            image_keys=image_keys,
            graded_at=datetime.now(UTC),
        )

    @classmethod
    def create_for_human_review(
        cls,
        return_id: ReturnId,
        confidence: float,
        damage_labels: list[DamageLabel],
        image_keys: list[ImageKey],
    ) -> ConditionGrade:
        return cls(
            return_id=return_id,
            grade=Grade.C,
            confidence=ConfidenceScore.of(confidence),
            damage_labels=damage_labels,
            damage_description="Confidence too low for automated grading - human review required.",
            image_keys=image_keys,
            graded_at=datetime.now(UTC),
            routed_to_human_review=True,
        )

    def meets_confidence_threshold(self, threshold: float) -> bool:
        return self._confidence.meets_threshold(threshold)

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def grade(self) -> Grade:
        return self._grade

    @property
    def confidence(self) -> ConfidenceScore:
        return self._confidence

    @property
    def damage_labels(self) -> list[DamageLabel]:
        return list(self._damage_labels)

    @property
    def damage_description(self) -> str:
        return self._damage_description

    @property
    def image_keys(self) -> list[ImageKey]:
        return list(self._image_keys)

    @property
    def graded_at(self) -> datetime:
        return self._graded_at

    @property
    def routed_to_human_review(self) -> bool:
        return self._routed_to_human_review

    @property
    def primary_damage(self) -> DamageLabel | None:
        if not self._damage_labels:
            return None
        return max(self._damage_labels, key=lambda d: d.confidence)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConditionGrade):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)

    def __repr__(self) -> str:
        return (
            f"ConditionGrade(return_id={self._return_id}, grade={self._grade.value}, "
            f"confidence={self._confidence})"
        )
