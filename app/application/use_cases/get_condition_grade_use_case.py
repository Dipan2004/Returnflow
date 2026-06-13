# app/application/use_cases/get_condition_grade_use_case.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.use_cases.dto import ConditionGradeResult, DamageLabelDTO
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetConditionGradeUseCase:
    def __init__(self, condition_grade_repository: ConditionGradeRepository) -> None:
        self._repository = condition_grade_repository

    async def execute(self, return_id_str: str) -> ConditionGradeResult:
        return_id = ReturnId(return_id_str)
        grade = await self._repository.get_by_return_id(return_id)
        if grade is None:
            raise EntityNotFoundError("ConditionGrade", return_id_str)
        return ConditionGradeResult(
            return_id=return_id_str,
            grade=grade.grade.value,
            confidence=grade.confidence.value,
            damage_labels=[
                DamageLabelDTO(name=d.name, confidence=d.confidence)
                for d in grade.damage_labels
            ],
            damage_description=grade.damage_description,
            routed_to_human_review=grade.routed_to_human_review,
            graded_at=grade.graded_at,
        )