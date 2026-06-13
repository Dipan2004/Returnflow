from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade


@dataclass(frozen=True)
class GradingResult:
    grade: Grade
    confidence: float
    damage_labels: list[DamageLabel]
    raw_label_count: int


@dataclass(frozen=True)
class DamageDescriptionResult:
    description: str
    model_id: str


class GradingPort(ABC):
    @abstractmethod
    async def grade_images(
        self,
        bucket: str,
        image_keys: list[str],
    ) -> GradingResult: ...

    @abstractmethod
    async def describe_damage(
        self,
        grade: Grade,
        damage_labels: list[DamageLabel],
    ) -> DamageDescriptionResult: ...