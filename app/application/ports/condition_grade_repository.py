# app/application/ports/condition_grade_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.condition_grade import ConditionGrade
from app.domain.value_objects.return_id import ReturnId


class ConditionGradeRepository(ABC):
    @abstractmethod
    async def save(self, condition_grade: ConditionGrade) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> ConditionGrade | None: ...