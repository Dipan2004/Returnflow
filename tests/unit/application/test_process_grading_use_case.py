# tests/unit/application/test_process_grading_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.domain.entities.condition_grade import DamageLabel
from app.domain.exceptions import EntityNotFoundError
from app.domain.services.human_review_decision import ConfidenceGate
from app.domain.value_objects.grade import Grade
from tests.factories.domain_factories import make_return_request
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.fakes.fake_grading_port import FakeGradingPort
from tests.fakes.fake_return_repository import FakeReturnRepository


def _make_use_case(
    grading_port: FakeGradingPort,
    threshold: float = 87.0,
) -> tuple[ProcessGradingUseCase, FakeConditionGradeRepository, FakeReturnRepository]:
    repo = FakeReturnRepository()
    grade_repo = FakeConditionGradeRepository()
    use_case = ProcessGradingUseCase(
        grading_port=grading_port,
        condition_grade_repository=grade_repo,
        return_repository=repo,
        confidence_gate=ConfidenceGate(threshold=threshold),
        image_bucket="test-bucket",
    )
    return use_case, grade_repo, repo


@pytest.mark.asyncio
async def test_process_grading_happy_path() -> None:
    return_request = make_return_request()
    port = FakeGradingPort(grade=Grade.A, confidence=95.0)
    use_case, grade_repo, repo = _make_use_case(port)
    await repo.save(return_request)

    result = await use_case.execute(return_request.return_id.value)

    assert result.grade == "A"
    assert result.confidence == 95.0
    assert not result.routed_to_human_review
    saved = await grade_repo.get_by_return_id(return_request.return_id)
    assert saved is not None
    assert saved.grade == Grade.A


@pytest.mark.asyncio
async def test_process_grading_routes_to_human_review_below_threshold() -> None:
    return_request = make_return_request()
    port = FakeGradingPort(grade=Grade.B, confidence=70.0)
    use_case, grade_repo, repo = _make_use_case(port, threshold=87.0)
    await repo.save(return_request)

    result = await use_case.execute(return_request.return_id.value)

    assert result.routed_to_human_review
    saved = await grade_repo.get_by_return_id(return_request.return_id)
    assert saved is not None
    assert saved.routed_to_human_review


@pytest.mark.asyncio
async def test_process_grading_raises_when_return_not_found() -> None:
    port = FakeGradingPort()
    use_case, _, _ = _make_use_case(port)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute("nonexistent-id")


@pytest.mark.asyncio
async def test_process_grading_persists_damage_labels() -> None:
    return_request = make_return_request()
    labels = [DamageLabel(name="Scratch", confidence=82.0)]
    port = FakeGradingPort(grade=Grade.B, confidence=88.0, damage_labels=labels)
    use_case, grade_repo, repo = _make_use_case(port)
    await repo.save(return_request)

    result = await use_case.execute(return_request.return_id.value)

    assert len(result.damage_labels) == 1
    assert result.damage_labels[0].name == "Scratch"


@pytest.mark.asyncio
async def test_process_grading_uses_grading_port_description() -> None:
    return_request = make_return_request()
    port = FakeGradingPort(
        grade=Grade.A,
        confidence=91.0,
        description="Minor scuffing on the front panel.",
    )
    use_case, _, repo = _make_use_case(port)
    await repo.save(return_request)

    result = await use_case.execute(return_request.return_id.value)

    assert port.grade_calls == [("test-bucket", [key.value for key in return_request.image_keys])]
    assert result.damage_description == "Minor scuffing on the front panel."
