# app/api/routers/grades.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas.grade_schemas import (
    ConditionGradeResponse,
    DamageLabelResponse,
    ProcessGradingRequest,
    ProcessGradingResponse,
    ReviewStatusResponse,
    StepRecordResponse,
    WorkflowStateResponse,
)
from app.application.services.grading_workflow_service import GradingWorkflowService
from app.application.use_cases.get_condition_grade_use_case import GetConditionGradeUseCase
from app.application.use_cases.get_review_status_use_case import GetReviewStatusUseCase
from app.application.use_cases.get_workflow_state_use_case import GetWorkflowStateUseCase
from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.container import Container

router = APIRouter(prefix="/grades", tags=["grading"])


@router.post("/process", response_model=ProcessGradingResponse, status_code=200)
@inject
async def process_grading_workflow(
    body: ProcessGradingRequest,
    service: GradingWorkflowService = Depends(Provide[Container.grading_workflow_service]),
) -> ProcessGradingResponse:
    result = await service.execute(body.return_id)
    return ProcessGradingResponse(
        return_id=result.return_id,
        grade=result.grade,
        confidence=result.confidence,
        damage_labels=[
            DamageLabelResponse(name=d.name, confidence=d.confidence)
            for d in result.damage_labels
        ],
        damage_description=result.damage_description,
        routed_to_human_review=result.routed_to_human_review,
        graded_at=result.graded_at,
    )


@router.post("", response_model=ProcessGradingResponse, status_code=200)
@inject
async def process_grading(
    body: ProcessGradingRequest,
    use_case: ProcessGradingUseCase = Depends(Provide[Container.process_grading_use_case]),
) -> ProcessGradingResponse:
    result = await use_case.execute(body.return_id)
    return ProcessGradingResponse(
        return_id=result.return_id,
        grade=result.grade,
        confidence=result.confidence,
        damage_labels=[
            DamageLabelResponse(name=d.name, confidence=d.confidence)
            for d in result.damage_labels
        ],
        damage_description=result.damage_description,
        routed_to_human_review=result.routed_to_human_review,
        graded_at=result.graded_at,
    )


@router.get("/{return_id}", response_model=ConditionGradeResponse, status_code=200)
@inject
async def get_condition_grade(
    return_id: str,
    use_case: GetConditionGradeUseCase = Depends(
        Provide[Container.get_condition_grade_use_case]
    ),
) -> ConditionGradeResponse:
    result = await use_case.execute(return_id)
    return ConditionGradeResponse(
        return_id=result.return_id,
        grade=result.grade,
        confidence=result.confidence,
        damage_labels=[
            DamageLabelResponse(name=d.name, confidence=d.confidence)
            for d in result.damage_labels
        ],
        damage_description=result.damage_description,
        routed_to_human_review=result.routed_to_human_review,
        graded_at=result.graded_at,
    )


@router.get(
    "/{return_id}/workflow", response_model=WorkflowStateResponse, status_code=200
)
@inject
async def get_workflow_state(
    return_id: str,
    use_case: GetWorkflowStateUseCase = Depends(
        Provide[Container.get_workflow_state_use_case]
    ),
) -> WorkflowStateResponse:
    result = await use_case.execute(return_id)
    return WorkflowStateResponse(
        return_id=result.return_id,
        status=result.status,
        current_step=result.current_step,
        steps=[
            StepRecordResponse(
                step=s.step,
                status=s.status,
                started_at=s.started_at,
                completed_at=s.completed_at,
                duration_ms=s.duration_ms,
                error_message=s.error_message,
            )
            for s in result.steps
        ],
        started_at=result.started_at,
        completed_at=result.completed_at,
        total_duration_ms=result.total_duration_ms,
        error_message=result.error_message,
    )


@router.get(
    "/{return_id}/review-status", response_model=ReviewStatusResponse, status_code=200
)
@inject
async def get_review_status(
    return_id: str,
    use_case: GetReviewStatusUseCase = Depends(
        Provide[Container.get_review_status_use_case]
    ),
) -> ReviewStatusResponse:
    result = await use_case.execute(return_id)
    return ReviewStatusResponse(
        return_id=result.return_id,
        routed_to_human_review=result.routed_to_human_review,
        confidence=result.confidence,
        grade=result.grade,
        workflow_status=result.workflow_status,
        graded_at=result.graded_at,
    )
