# app/application/use_cases/get_review_status_use_case.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.workflow_state_repository import WorkflowStateRepository
from app.application.use_cases.dto import ReviewStatusResult
from app.domain.entities.workflow_state import WorkflowStatus
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetReviewStatusUseCase:
    def __init__(
        self,
        condition_grade_repository: ConditionGradeRepository,
        workflow_state_repository: WorkflowStateRepository,
    ) -> None:
        self._grade_repository = condition_grade_repository
        self._workflow_repository = workflow_state_repository

    async def execute(self, return_id_str: str) -> ReviewStatusResult:
        return_id = ReturnId(return_id_str)
        grade = await self._grade_repository.get_by_return_id(return_id)
        if grade is None:
            raise EntityNotFoundError("ConditionGrade", return_id_str)

        workflow = await self._workflow_repository.get_by_return_id(return_id)
        workflow_status = workflow.status.value if workflow else WorkflowStatus.NOT_STARTED.value

        return ReviewStatusResult(
            return_id=return_id_str,
            routed_to_human_review=grade.routed_to_human_review,
            confidence=grade.confidence.value,
            grade=grade.grade.value,
            workflow_status=workflow_status,
            graded_at=grade.graded_at,
        )
