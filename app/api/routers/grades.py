# app/api/routers/grades.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.schemas.grade_schemas import (
    ConditionGradeResponse,
    DamageLabelResponse,
    ProcessGradingRequest,
    ProcessGradingResponse,
)
from app.application.use_cases.get_condition_grade_use_case import GetConditionGradeUseCase
from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.container import Container

router = APIRouter(prefix="/grades", tags=["grading"])


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