# app/application/ports/description_generation_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade


@dataclass(frozen=True)
class DescriptionRequest:
    grade: Grade
    damage_labels: list[DamageLabel]
    sku_id: str | None = None


@dataclass(frozen=True)
class DescriptionResponse:
    description: str
    model_id: str
    word_count: int
    used_fallback: bool


class DescriptionGenerationPort(ABC):
    @abstractmethod
    async def generate(self, request: DescriptionRequest) -> DescriptionResponse: ...