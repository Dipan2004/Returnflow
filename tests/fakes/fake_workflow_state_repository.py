# tests/fakes/fake_workflow_state_repository.py
from __future__ import annotations

from app.application.ports.workflow_state_repository import WorkflowStateRepository
from app.domain.entities.workflow_state import WorkflowState
from app.domain.value_objects.return_id import ReturnId


class FakeWorkflowStateRepository(WorkflowStateRepository):
    def __init__(self) -> None:
        self._store: dict[str, WorkflowState] = {}

    async def save(self, workflow_state: WorkflowState) -> None:
        self._store[workflow_state.return_id.value] = workflow_state

    async def get_by_return_id(self, return_id: ReturnId) -> WorkflowState | None:
        return self._store.get(return_id.value)
