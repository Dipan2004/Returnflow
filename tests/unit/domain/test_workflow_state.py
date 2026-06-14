# tests/unit/domain/test_workflow_state.py
from __future__ import annotations

import pytest

from app.domain.entities.workflow_state import WorkflowState, WorkflowStatus, WorkflowStep
from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


def _make_workflow() -> WorkflowState:
    return WorkflowState.create(ReturnId("TEST123"))


def test_create_starts_in_progress() -> None:
    workflow = _make_workflow()
    assert workflow.status == WorkflowStatus.IN_PROGRESS
    assert workflow.current_step == WorkflowStep.GRADE_IMAGES
    assert workflow.started_at is not None


def test_record_step_start_and_complete() -> None:
    workflow = _make_workflow()
    workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
    workflow.record_step_complete(
        WorkflowStep.GRADE_IMAGES, metadata={"grade": "A"}
    )
    assert len(workflow.steps) == 1
    assert workflow.steps[0].status == "COMPLETED"
    assert workflow.steps[0].metadata == {"grade": "A"}


def test_record_step_failed_sets_workflow_failed() -> None:
    workflow = _make_workflow()
    workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
    workflow.record_step_failed(WorkflowStep.GRADE_IMAGES, "Rekognition timeout")
    assert workflow.status == WorkflowStatus.FAILED
    assert workflow.error_message == "Rekognition timeout"
    assert workflow.completed_at is not None


def test_mark_completed() -> None:
    workflow = _make_workflow()
    workflow.mark_completed()
    assert workflow.status == WorkflowStatus.COMPLETED
    assert workflow.current_step == WorkflowStep.COMPLETED
    assert workflow.completed_at is not None


def test_mark_sent_to_review() -> None:
    workflow = _make_workflow()
    workflow.mark_sent_to_review()
    assert workflow.status == WorkflowStatus.SENT_TO_REVIEW
    assert workflow.current_step == WorkflowStep.SEND_TO_HUMAN_REVIEW


def test_total_duration_ms_none_when_not_completed() -> None:
    workflow = _make_workflow()
    assert workflow.total_duration_ms is None


def test_total_duration_ms_computed_when_completed() -> None:
    workflow = _make_workflow()
    workflow.mark_completed()
    assert workflow.total_duration_ms is not None
    assert workflow.total_duration_ms >= 0


def test_record_step_complete_raises_when_no_matching_in_progress() -> None:
    workflow = _make_workflow()
    with pytest.raises(DomainValidationError, match="No in-progress step"):
        workflow.record_step_complete(WorkflowStep.GRADE_IMAGES)


def test_step_record_duration_ms() -> None:
    workflow = _make_workflow()
    workflow.record_step_start(WorkflowStep.CHECK_CONFIDENCE)
    workflow.record_step_complete(WorkflowStep.CHECK_CONFIDENCE)
    step = workflow.steps[0]
    assert step.duration_ms is not None
    assert step.duration_ms >= 0
