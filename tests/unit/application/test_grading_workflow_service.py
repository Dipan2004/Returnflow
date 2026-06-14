# tests/unit/application/test_grading_workflow_service.py
from __future__ import annotations

import pytest

from app.application.services.grading_workflow_service import GradingWorkflowService
from app.domain.entities.condition_grade import DamageLabel
from app.domain.entities.workflow_state import WorkflowStatus
from app.domain.exceptions import EntityNotFoundError, InfrastructureError
from app.domain.services.human_review_decision import ConfidenceGate
from app.domain.value_objects.grade import Grade
from tests.factories.domain_factories import make_return_request
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.fakes.fake_grading_port import FakeGradingPort
from tests.fakes.fake_human_review_queue_port import FakeHumanReviewQueuePort
from tests.fakes.fake_return_repository import FakeReturnRepository
from tests.fakes.fake_workflow_state_repository import FakeWorkflowStateRepository


def _make_service(
    grading_port: FakeGradingPort | None = None,
    threshold: float = 87.0,
    queue_should_fail: bool = False,
) -> tuple[
    GradingWorkflowService,
    FakeConditionGradeRepository,
    FakeReturnRepository,
    FakeWorkflowStateRepository,
    FakeHumanReviewQueuePort,
]:
    port = grading_port or FakeGradingPort(grade=Grade.A, confidence=95.0)
    return_repo = FakeReturnRepository()
    grade_repo = FakeConditionGradeRepository()
    workflow_repo = FakeWorkflowStateRepository()
    queue = FakeHumanReviewQueuePort(should_fail=queue_should_fail)
    service = GradingWorkflowService(
        grading_port=port,
        condition_grade_repository=grade_repo,
        return_repository=return_repo,
        workflow_state_repository=workflow_repo,
        human_review_queue=queue,
        confidence_gate=ConfidenceGate(threshold=threshold),
        image_bucket="test-bucket",
    )
    return service, grade_repo, return_repo, workflow_repo, queue


@pytest.mark.asyncio
async def test_workflow_happy_path_completes() -> None:
    port = FakeGradingPort(grade=Grade.A, confidence=95.0)
    service, grade_repo, return_repo, workflow_repo, queue = _make_service(port)
    return_request = make_return_request()
    await return_repo.save(return_request)

    result = await service.execute(return_request.return_id.value)

    assert result.grade == "A"
    assert result.confidence == 95.0
    assert not result.routed_to_human_review

    workflow = await workflow_repo.get_by_return_id(return_request.return_id)
    assert workflow is not None
    assert workflow.status == WorkflowStatus.COMPLETED
    assert len(workflow.steps) == 3
    assert len(queue.published) == 0


@pytest.mark.asyncio
async def test_workflow_routes_to_human_review_below_threshold() -> None:
    port = FakeGradingPort(grade=Grade.B, confidence=70.0)
    service, grade_repo, return_repo, workflow_repo, queue = _make_service(port)
    return_request = make_return_request()
    await return_repo.save(return_request)

    result = await service.execute(return_request.return_id.value)

    assert result.routed_to_human_review
    assert len(queue.published) == 1
    assert queue.published[0].return_id == return_request.return_id

    workflow = await workflow_repo.get_by_return_id(return_request.return_id)
    assert workflow is not None
    assert workflow.status == WorkflowStatus.SENT_TO_REVIEW


@pytest.mark.asyncio
async def test_workflow_raises_when_return_not_found() -> None:
    service, _, _, _, _ = _make_service()
    with pytest.raises(EntityNotFoundError):
        await service.execute("nonexistent-id")


@pytest.mark.asyncio
async def test_workflow_persists_condition_grade() -> None:
    labels = [DamageLabel(name="Scratch", confidence=82.0)]
    port = FakeGradingPort(grade=Grade.B, confidence=88.0, damage_labels=labels)
    service, grade_repo, return_repo, _, _ = _make_service(port)
    return_request = make_return_request()
    await return_repo.save(return_request)

    await service.execute(return_request.return_id.value)

    saved = await grade_repo.get_by_return_id(return_request.return_id)
    assert saved is not None
    assert saved.grade == Grade.B
    assert len(saved.damage_labels) == 1


@pytest.mark.asyncio
async def test_workflow_records_step_metadata() -> None:
    port = FakeGradingPort(grade=Grade.A, confidence=92.0)
    service, _, return_repo, workflow_repo, _ = _make_service(port)
    return_request = make_return_request()
    await return_repo.save(return_request)

    await service.execute(return_request.return_id.value)

    workflow = await workflow_repo.get_by_return_id(return_request.return_id)
    assert workflow is not None
    grade_step = workflow.steps[0]
    assert grade_step.metadata["grade"] == "A"
    assert grade_step.metadata["confidence"] == 92.0


@pytest.mark.asyncio
async def test_workflow_fails_when_grading_port_raises() -> None:
    port = FakeGradingPort(grade=Grade.A, confidence=95.0)
    service, _, return_repo, workflow_repo, _ = _make_service(port)
    return_request = make_return_request()
    await return_repo.save(return_request)

    port.grade_images = _raise_infra_error  # type: ignore[assignment]

    with pytest.raises(InfrastructureError):
        await service.execute(return_request.return_id.value)

    workflow = await workflow_repo.get_by_return_id(return_request.return_id)
    assert workflow is not None
    assert workflow.status == WorkflowStatus.FAILED


@pytest.mark.asyncio
async def test_workflow_fails_when_sqs_publish_fails() -> None:
    port = FakeGradingPort(grade=Grade.B, confidence=70.0)
    service, _, return_repo, workflow_repo, _ = _make_service(port, queue_should_fail=True)
    return_request = make_return_request()
    await return_repo.save(return_request)

    with pytest.raises(InfrastructureError):
        await service.execute(return_request.return_id.value)

    workflow = await workflow_repo.get_by_return_id(return_request.return_id)
    assert workflow is not None
    assert workflow.status == WorkflowStatus.FAILED


async def _raise_infra_error(bucket: str, image_keys: list[str]) -> None:
    raise InfrastructureError("Rekognition", "Connection timeout")
