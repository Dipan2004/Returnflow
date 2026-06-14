# app/application/ports/grading_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade


@dataclass(frozen=True)
class GradingResult:
    grade: Grade
    confidence: float
    damage_labels: list[DamageLabel]
    damage_description: str
    raw_label_count: int
    description_used_fallback: bool = field(default=False)


class GradingPort(ABC):
    @abstractmethod
    async def grade_images(
        self,
        bucket: str,
        image_keys: list[str],
    ) -> GradingResult: ...