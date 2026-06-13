# tests/unit/application/test_get_condition_grade_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.get_condition_grade_use_case import GetConditionGradeUseCase
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.return_id import ReturnId
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.factories.domain_factories import make_return_request


def _make_grade(return_id: ReturnId) -> ConditionGrade:
    return ConditionGrade.create(
        return_id=return_id,
        grade=Grade.A,
        confidence=92.0,
        damage_labels=[],
        damage_description="No damage.",
        image_keys=[],
    )


@pytest.mark.asyncio
async def test_get_condition_grade_returns_result() -> None:
    repo = FakeConditionGradeRepository()
    return_request = make_return_request()
    grade = _make_grade(return_request.return_id)
    await repo.save(grade)

    use_case = GetConditionGradeUseCase(condition_grade_repository=repo)
    result = await use_case.execute(return_request.return_id.value)

    assert result.return_id == return_request.return_id.value
    assert result.grade == "A"
    assert result.confidence == 92.0


@pytest.mark.asyncio
async def test_get_condition_grade_raises_when_not_found() -> None:
    repo = FakeConditionGradeRepository()
    use_case = GetConditionGradeUseCase(condition_grade_repository=repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute("missing-id")