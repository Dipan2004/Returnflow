# app/application/ports/workflow_state_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.workflow_state import WorkflowState
from app.domain.value_objects.return_id import ReturnId


class WorkflowStateRepository(ABC):
    @abstractmethod
    async def save(self, workflow_state: WorkflowState) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> WorkflowState | None: ...
