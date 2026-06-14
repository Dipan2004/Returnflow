# app/application/use_cases/get_workflow_state_use_case.py
from __future__ import annotations

from app.application.ports.workflow_state_repository import WorkflowStateRepository
from app.application.use_cases.dto import StepRecordDTO, WorkflowStateResult
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetWorkflowStateUseCase:
    def __init__(self, workflow_state_repository: WorkflowStateRepository) -> None:
        self._repository = workflow_state_repository

    async def execute(self, return_id_str: str) -> WorkflowStateResult:
        return_id = ReturnId(return_id_str)
        state = await self._repository.get_by_return_id(return_id)
        if state is None:
            raise EntityNotFoundError("WorkflowState", return_id_str)
        return WorkflowStateResult(
            return_id=return_id_str,
            status=state.status.value,
            current_step=state.current_step.value if state.current_step else None,
            steps=[
                StepRecordDTO(
                    step=s.step.value,
                    status=s.status,
                    started_at=s.started_at,
                    completed_at=s.completed_at,
                    duration_ms=s.duration_ms,
                    error_message=s.error_message,
                )
                for s in state.steps
            ],
            started_at=state.started_at,
            completed_at=state.completed_at,
            total_duration_ms=state.total_duration_ms,
            error_message=state.error_message,
        )
