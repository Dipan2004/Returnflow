# app/infrastructure/persistence/in_memory_condition_grade_repository.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryConditionGradeRepository(ConditionGradeRepository):
    def __init__(self) -> None:
        STORE.setdefault("grades", {})

    async def save(self, condition_grade: ConditionGrade) -> None:
        STORE["grades"][condition_grade.return_id.value] = condition_grade

    async def get_by_return_id(self, return_id: ReturnId) -> ConditionGrade | None:
        return STORE["grades"].get(return_id.value)
