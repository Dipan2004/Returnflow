# app/infrastructure/persistence/workflow_state_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.workflow_state import (
    StepRecord,
    WorkflowState,
    WorkflowStatus,
    WorkflowStep,
)
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_WORKFLOW_STATE = "WORKFLOW_STATE"


def workflow_state_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def workflow_state_sk() -> str:
    return "WORKFLOW_STATE"


def to_item(workflow_state: WorkflowState) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": workflow_state_pk(workflow_state.return_id),
        "SK": workflow_state_sk(),
        "entity_type": ENTITY_TYPE_WORKFLOW_STATE,
        "return_id": workflow_state.return_id.value,
        "status": workflow_state.status.value,
        "current_step": workflow_state.current_step.value if workflow_state.current_step else None,
        "steps": [_step_to_dict(s) for s in workflow_state.steps],
    }
    if workflow_state.started_at:
        item["started_at"] = workflow_state.started_at.isoformat()
    if workflow_state.completed_at:
        item["completed_at"] = workflow_state.completed_at.isoformat()
    if workflow_state.error_message:
        item["error_message"] = workflow_state.error_message
    return item


def from_item(item: dict[str, Any]) -> WorkflowState:
    return WorkflowState(
        return_id=ReturnId(item["return_id"]),
        status=WorkflowStatus(item["status"]),
        current_step=WorkflowStep(item["current_step"]) if item.get("current_step") else None,
        steps=[_step_from_dict(s) for s in item.get("steps", [])],
        started_at=_parse_datetime(item.get("started_at")),
        completed_at=_parse_datetime(item.get("completed_at")),
        error_message=item.get("error_message"),
    )


def _step_to_dict(step: StepRecord) -> dict[str, Any]:
    result: dict[str, Any] = {
        "step": step.step.value,
        "status": step.status,
        "started_at": step.started_at.isoformat(),
    }
    if step.completed_at:
        result["completed_at"] = step.completed_at.isoformat()
    if step.error_message:
        result["error_message"] = step.error_message
    if step.metadata:
        result["metadata"] = step.metadata
    return result


def _step_from_dict(data: dict[str, Any]) -> StepRecord:
    return StepRecord(
        step=WorkflowStep(data["step"]),
        status=data["status"],
        started_at=datetime.fromisoformat(data["started_at"]).replace(tzinfo=UTC),
        completed_at=_parse_datetime(data.get("completed_at")),
        error_message=data.get("error_message"),
        metadata=data.get("metadata", {}),
    )


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=UTC)
