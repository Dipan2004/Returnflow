# app/api/schemas/grade_schemas.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DamageLabelResponse(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=100.0)


class ProcessGradingRequest(BaseModel):
    return_id: str = Field(min_length=1)


class ProcessGradingResponse(BaseModel):
    return_id: str
    grade: str
    confidence: float
    damage_labels: list[DamageLabelResponse]
    damage_description: str
    routed_to_human_review: bool
    graded_at: datetime


class ConditionGradeResponse(BaseModel):
    return_id: str
    grade: str
    confidence: float
    damage_labels: list[DamageLabelResponse]
    damage_description: str
    routed_to_human_review: bool
    graded_at: datetime


class StepRecordResponse(BaseModel):
    step: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
    error_message: str | None = None


class WorkflowStateResponse(BaseModel):
    return_id: str
    status: str
    current_step: str | None
    steps: list[StepRecordResponse]
    started_at: datetime | None
    completed_at: datetime | None
    total_duration_ms: int | None
    error_message: str | None = None


class ReviewStatusResponse(BaseModel):
    return_id: str
    routed_to_human_review: bool
    confidence: float
    grade: str
    workflow_status: str
    graded_at: datetime
