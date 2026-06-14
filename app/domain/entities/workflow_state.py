# app/domain/entities/workflow_state.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


class WorkflowStep(StrEnum):
    GRADE_IMAGES = "GRADE_IMAGES"
    CHECK_CONFIDENCE = "CHECK_CONFIDENCE"
    GENERATE_DAMAGE_DESCRIPTION = "GENERATE_DAMAGE_DESCRIPTION"
    SEND_TO_HUMAN_REVIEW = "SEND_TO_HUMAN_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SENT_TO_REVIEW = "SENT_TO_REVIEW"


@dataclass(frozen=True)
class StepRecord:
    step: WorkflowStep
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def duration_ms(self) -> int | None:
        if self.completed_at is None:
            return None
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() * 1000)


class WorkflowState:
    def __init__(
        self,
        return_id: ReturnId,
        status: WorkflowStatus = WorkflowStatus.NOT_STARTED,
        current_step: WorkflowStep | None = None,
        steps: list[StepRecord] | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        error_message: str | None = None,
    ) -> None:
        self._return_id = return_id
        self._status = status
        self._current_step = current_step
        self._steps: list[StepRecord] = steps or []
        self._started_at = started_at
        self._completed_at = completed_at
        self._error_message = error_message

    @classmethod
    def create(cls, return_id: ReturnId) -> WorkflowState:
        return cls(
            return_id=return_id,
            status=WorkflowStatus.IN_PROGRESS,
            current_step=WorkflowStep.GRADE_IMAGES,
            started_at=datetime.now(UTC),
        )

    def record_step_start(self, step: WorkflowStep) -> None:
        self._current_step = step
        self._steps.append(
            StepRecord(
                step=step,
                status="IN_PROGRESS",
                started_at=datetime.now(UTC),
            )
        )

    def record_step_complete(
        self, step: WorkflowStep, metadata: dict[str, object] | None = None
    ) -> None:
        for i in range(len(self._steps) - 1, -1, -1):
            if self._steps[i].step == step and self._steps[i].status == "IN_PROGRESS":
                completed = StepRecord(
                    step=step,
                    status="COMPLETED",
                    started_at=self._steps[i].started_at,
                    completed_at=datetime.now(UTC),
                    metadata=metadata or {},
                )
                self._steps[i] = completed
                return
        raise DomainValidationError(f"No in-progress step record found for {step.value}")

    def record_step_failed(self, step: WorkflowStep, error: str) -> None:
        for i in range(len(self._steps) - 1, -1, -1):
            if self._steps[i].step == step and self._steps[i].status == "IN_PROGRESS":
                failed = StepRecord(
                    step=step,
                    status="FAILED",
                    started_at=self._steps[i].started_at,
                    completed_at=datetime.now(UTC),
                    error_message=error,
                )
                self._steps[i] = failed
                break
        self._status = WorkflowStatus.FAILED
        self._error_message = error
        self._completed_at = datetime.now(UTC)

    def mark_completed(self) -> None:
        self._status = WorkflowStatus.COMPLETED
        self._current_step = WorkflowStep.COMPLETED
        self._completed_at = datetime.now(UTC)

    def mark_sent_to_review(self) -> None:
        self._status = WorkflowStatus.SENT_TO_REVIEW
        self._current_step = WorkflowStep.SEND_TO_HUMAN_REVIEW
        self._completed_at = datetime.now(UTC)

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def status(self) -> WorkflowStatus:
        return self._status

    @property
    def current_step(self) -> WorkflowStep | None:
        return self._current_step

    @property
    def steps(self) -> list[StepRecord]:
        return list(self._steps)

    @property
    def started_at(self) -> datetime | None:
        return self._started_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def error_message(self) -> str | None:
        return self._error_message

    @property
    def total_duration_ms(self) -> int | None:
        if self._started_at is None or self._completed_at is None:
            return None
        delta = self._completed_at - self._started_at
        return int(delta.total_seconds() * 1000)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkflowState):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)
