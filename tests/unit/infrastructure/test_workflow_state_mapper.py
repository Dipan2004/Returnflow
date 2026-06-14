# tests/unit/infrastructure/test_workflow_state_mapper.py
from __future__ import annotations

from app.domain.entities.workflow_state import WorkflowState, WorkflowStatus, WorkflowStep
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.workflow_state_mapper import from_item, to_item


def test_to_item_contains_required_keys() -> None:
    workflow = WorkflowState.create(ReturnId("TEST123"))
    item = to_item(workflow)

    assert item["PK"] == "RETURN#TEST123"
    assert item["SK"] == "WORKFLOW_STATE"
    assert item["entity_type"] == "WORKFLOW_STATE"
    assert item["return_id"] == "TEST123"
    assert item["status"] == "IN_PROGRESS"
    assert item["current_step"] == "GRADE_IMAGES"


def test_to_item_includes_steps() -> None:
    workflow = WorkflowState.create(ReturnId("TEST456"))
    workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
    workflow.record_step_complete(WorkflowStep.GRADE_IMAGES, metadata={"grade": "A"})
    item = to_item(workflow)

    assert len(item["steps"]) == 1
    assert item["steps"][0]["step"] == "GRADE_IMAGES"
    assert item["steps"][0]["status"] == "COMPLETED"


def test_from_item_roundtrip() -> None:
    workflow = WorkflowState.create(ReturnId("TEST789"))
    workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
    workflow.record_step_complete(
        WorkflowStep.GRADE_IMAGES, metadata={"grade": "B", "confidence": 88.0}
    )
    workflow.record_step_start(WorkflowStep.CHECK_CONFIDENCE)
    workflow.record_step_complete(WorkflowStep.CHECK_CONFIDENCE)
    workflow.mark_completed()

    item = to_item(workflow)
    restored = from_item(item)

    assert restored.return_id == workflow.return_id
    assert restored.status == WorkflowStatus.COMPLETED
    assert restored.current_step == WorkflowStep.COMPLETED
    assert len(restored.steps) == 2
    assert restored.steps[0].step == WorkflowStep.GRADE_IMAGES
    assert restored.completed_at is not None


def test_from_item_with_failed_state() -> None:
    workflow = WorkflowState.create(ReturnId("TESTFAIL"))
    workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
    workflow.record_step_failed(WorkflowStep.GRADE_IMAGES, "Timeout error")

    item = to_item(workflow)
    restored = from_item(item)

    assert restored.status == WorkflowStatus.FAILED
    assert restored.error_message == "Timeout error"
    assert restored.steps[0].error_message == "Timeout error"


def test_from_item_with_no_current_step() -> None:
    item = {
        "PK": "RETURN#TESTNULL",
        "SK": "WORKFLOW_STATE",
        "entity_type": "WORKFLOW_STATE",
        "return_id": "TESTNULL",
        "status": "NOT_STARTED",
        "current_step": None,
        "steps": [],
    }
    restored = from_item(item)
    assert restored.current_step is None
    assert restored.status == WorkflowStatus.NOT_STARTED
