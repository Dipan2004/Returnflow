# app/infrastructure/persistence/in_memory_workflow_state_repository.py
from __future__ import annotations

from app.application.ports.workflow_state_repository import WorkflowStateRepository
from app.domain.entities.workflow_state import WorkflowState
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryWorkflowStateRepository(WorkflowStateRepository):
    def __init__(self) -> None:
        STORE.setdefault("workflow_states", {})

    async def save(self, workflow_state: WorkflowState) -> None:
        STORE["workflow_states"][workflow_state.return_id.value] = workflow_state

    async def get_by_return_id(self, return_id: ReturnId) -> WorkflowState | None:
        return STORE["workflow_states"].get(return_id.value)
