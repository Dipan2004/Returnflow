# tests/unit/application/test_get_review_status_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.get_review_status_use_case import GetReviewStatusUseCase
from app.domain.entities.condition_grade import ConditionGrade, DamageLabel
from app.domain.entities.workflow_state import WorkflowState
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.fakes.fake_workflow_state_repository import FakeWorkflowStateRepository


def _make_grade(return_id: str, routed: bool = False) -> ConditionGrade:
    rid = ReturnId(return_id)
    if routed:
        return ConditionGrade.create_for_human_review(
            return_id=rid,
            confidence=70.0,
            damage_labels=[DamageLabel(name="Scratch", confidence=70.0)],
            image_keys=[ImageKey.pending(return_id, 1)],
        )
    return ConditionGrade.create(
        return_id=rid,
        grade=Grade.A,
        confidence=92.0,
        damage_labels=[],
        damage_description="No damage.",
        image_keys=[ImageKey.pending(return_id, 1)],
    )


@pytest.mark.asyncio
async def test_get_review_status_not_routed() -> None:
    grade_repo = FakeConditionGradeRepository()
    workflow_repo = FakeWorkflowStateRepository()
    grade = _make_grade("TEST123", routed=False)
    await grade_repo.save(grade)

    workflow = WorkflowState.create(ReturnId("TEST123"))
    workflow.mark_completed()
    await workflow_repo.save(workflow)

    use_case = GetReviewStatusUseCase(
        condition_grade_repository=grade_repo,
        workflow_state_repository=workflow_repo,
    )
    result = await use_case.execute("TEST123")

    assert not result.routed_to_human_review
    assert result.confidence == 92.0
    assert result.grade == "A"
    assert result.workflow_status == "COMPLETED"


@pytest.mark.asyncio
async def test_get_review_status_routed_to_review() -> None:
    grade_repo = FakeConditionGradeRepository()
    workflow_repo = FakeWorkflowStateRepository()
    grade = _make_grade("TEST456", routed=True)
    await grade_repo.save(grade)

    workflow = WorkflowState.create(ReturnId("TEST456"))
    workflow.mark_sent_to_review()
    await workflow_repo.save(workflow)

    use_case = GetReviewStatusUseCase(
        condition_grade_repository=grade_repo,
        workflow_state_repository=workflow_repo,
    )
    result = await use_case.execute("TEST456")

    assert result.routed_to_human_review
    assert result.workflow_status == "SENT_TO_REVIEW"


@pytest.mark.asyncio
async def test_get_review_status_raises_not_found() -> None:
    grade_repo = FakeConditionGradeRepository()
    workflow_repo = FakeWorkflowStateRepository()
    use_case = GetReviewStatusUseCase(
        condition_grade_repository=grade_repo,
        workflow_state_repository=workflow_repo,
    )

    with pytest.raises(EntityNotFoundError):
        await use_case.execute("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_review_status_no_workflow_state() -> None:
    grade_repo = FakeConditionGradeRepository()
    workflow_repo = FakeWorkflowStateRepository()
    grade = _make_grade("TEST789", routed=False)
    await grade_repo.save(grade)

    use_case = GetReviewStatusUseCase(
        condition_grade_repository=grade_repo,
        workflow_state_repository=workflow_repo,
    )
    result = await use_case.execute("TEST789")

    assert result.workflow_status == "NOT_STARTED"
