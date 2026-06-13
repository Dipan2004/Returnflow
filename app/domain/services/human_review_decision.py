# app/domain/services/human_review_decision.py
from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.condition_grade import ConditionGrade


@dataclass(frozen=True)
class HumanReviewDecision:
    requires_review: bool
    reason: str

    @classmethod
    def approve(cls) -> HumanReviewDecision:
        return cls(requires_review=False, reason="")

    @classmethod
    def escalate(cls, confidence: float, threshold: float) -> HumanReviewDecision:
        return cls(
            requires_review=True,
            reason=(
                f"Confidence {confidence:.1f}% is below required threshold {threshold:.1f}%"
            ),
        )


class ConfidenceGate:
    def __init__(self, threshold: float) -> None:
        if not 0.0 <= threshold <= 100.0:
            raise ValueError(f"threshold must be 0-100, got {threshold}")
        self._threshold = threshold

    def evaluate(self, grade: ConditionGrade) -> HumanReviewDecision:
        if grade.meets_confidence_threshold(self._threshold):
            return HumanReviewDecision.approve()
        return HumanReviewDecision.escalate(
            confidence=grade.confidence.value,
            threshold=self._threshold,
        )

    @property
    def threshold(self) -> float:
        return self._threshold