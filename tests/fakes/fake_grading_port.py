# tests/fakes/fake_grading_port.py
from __future__ import annotations

from app.application.ports.grading_port import DamageDescriptionResult, GradingPort, GradingResult
from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade


class FakeGradingPort(GradingPort):
    def __init__(
        self,
        grade: Grade = Grade.A,
        confidence: float = 95.0,
        damage_labels: list[DamageLabel] | None = None,
        description: str = "No visible damage detected.",
    ) -> None:
        self.grade = grade
        self.confidence = confidence
        self.damage_labels = damage_labels or []
        self.description = description
        self.grade_calls: list[tuple[str, list[str]]] = []
        self.describe_calls: list[tuple[Grade, list[DamageLabel]]] = []

    async def grade_images(self, bucket: str, image_keys: list[str]) -> GradingResult:
        self.grade_calls.append((bucket, image_keys))
        return GradingResult(
            grade=self.grade,
            confidence=self.confidence,
            damage_labels=self.damage_labels,
            raw_label_count=len(self.damage_labels),
        )

    async def describe_damage(
        self, grade: Grade, damage_labels: list[DamageLabel]
    ) -> DamageDescriptionResult:
        self.describe_calls.append((grade, damage_labels))
        return DamageDescriptionResult(description=self.description, model_id="fake")