# tests/unit/application/test_get_workflow_state_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.get_workflow_state_use_case import GetWorkflowStateUseCase
from app.domain.entities.workflow_state import WorkflowState, WorkflowStep
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId
from tests.fakes.fake_workflow_state_repository import FakeWorkflowStateRepository


@pytest.mark.asyncio
async def test_get_workflow_state_returns_result() -> None:
    repo = FakeWorkflowStateRepository()
    return_id = ReturnId("TEST123")
    workflow = WorkflowState.create(return_id)
    workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
    workflow.record_step_complete(WorkflowStep.GRADE_IMAGES, metadata={"grade": "A"})
    workflow.mark_completed()
    await repo.save(workflow)

    use_case = GetWorkflowStateUseCase(workflow_state_repository=repo)
    result = await use_case.execute("TEST123")

    assert result.return_id == "TEST123"
    assert result.status == "COMPLETED"
    assert result.current_step == "COMPLETED"
    assert len(result.steps) == 1
    assert result.steps[0].step == "GRADE_IMAGES"
    assert result.steps[0].status == "COMPLETED"


@pytest.mark.asyncio
async def test_get_workflow_state_raises_not_found() -> None:
    repo = FakeWorkflowStateRepository()
    use_case = GetWorkflowStateUseCase(workflow_state_repository=repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute("NONEXISTENT")


@pytest.mark.asyncio
async def test_get_workflow_state_includes_timing() -> None:
    repo = FakeWorkflowStateRepository()
    return_id = ReturnId("TEST456")
    workflow = WorkflowState.create(return_id)
    workflow.record_step_start(WorkflowStep.CHECK_CONFIDENCE)
    workflow.record_step_complete(WorkflowStep.CHECK_CONFIDENCE)
    workflow.mark_completed()
    await repo.save(workflow)

    use_case = GetWorkflowStateUseCase(workflow_state_repository=repo)
    result = await use_case.execute("TEST456")

    assert result.total_duration_ms is not None
    assert result.total_duration_ms >= 0
    assert result.steps[0].duration_ms is not None
