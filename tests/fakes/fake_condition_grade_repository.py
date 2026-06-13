# tests/fakes/fake_condition_grade_repository.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.value_objects.return_id import ReturnId


class FakeConditionGradeRepository(ConditionGradeRepository):
    def __init__(self) -> None:
        self._store: dict[str, ConditionGrade] = {}

    async def save(self, condition_grade: ConditionGrade) -> None:
        self._store[condition_grade.return_id.value] = condition_grade

    async def get_by_return_id(self, return_id: ReturnId) -> ConditionGrade | None:
        return self._store.get(return_id.value)