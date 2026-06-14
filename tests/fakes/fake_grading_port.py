from __future__ import annotations

from app.application.ports.grading_port import GradingPort, GradingResult
from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade


class FakeGradingPort(GradingPort):
    def __init__(
        self,
        grade: Grade = Grade.A,
        confidence: float = 95.0,
        damage_labels: list[DamageLabel] | None = None,
        description: str = "No visible damage detected.",
        used_fallback: bool = False,
    ) -> None:
        self.grade = grade
        self.confidence = confidence
        self.damage_labels = damage_labels or []
        self.description = description
        self.used_fallback = used_fallback
        self.grade_calls: list[tuple[str, list[str]]] = []

    async def grade_images(self, bucket: str, image_keys: list[str]) -> GradingResult:
        self.grade_calls.append((bucket, image_keys))
        return GradingResult(
            grade=self.grade,
            confidence=self.confidence,
            damage_labels=self.damage_labels,
            damage_description=self.description,
            description_used_fallback=self.used_fallback,
            raw_label_count=len(self.damage_labels),
        )
