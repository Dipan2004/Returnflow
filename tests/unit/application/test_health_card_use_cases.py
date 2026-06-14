# tests/unit/application/test_health_card_use_cases.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.use_cases.generate_health_card_use_case import GenerateHealthCardUseCase
from app.application.use_cases.get_health_card_by_qr_use_case import GetHealthCardByQRUseCase
from app.application.use_cases.get_health_card_use_case import GetHealthCardUseCase
from app.domain.entities.condition_grade import ConditionGrade, DamageLabel
from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.entities.fraud_assessment import FraudAssessment, FraudSignal
from app.domain.exceptions import EntityNotFoundError, QRTokenNotFoundError
from app.domain.services.qr_generation_service import QRCodeGenerationService
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from tests.fakes.fake_condition_grade_repository import FakeConditionGradeRepository
from tests.fakes.fake_disposition_repository import FakeDispositionRepository
from tests.fakes.fake_fraud_repository import FakeFraudRepository
from tests.fakes.fake_health_card_repository import FakeHealthCardRepository
from tests.fakes.fake_qr_storage_port import FakeQRCodeStoragePort


def _grade(rid: ReturnId) -> ConditionGrade:
    return ConditionGrade(
        return_id=rid,
        grade=Grade.A,
        confidence=ConfidenceScore.of(92.0),
        damage_labels=[DamageLabel(name="Scratch", confidence=40.0)],
        damage_description="Minor scratch.",
        image_keys=[ImageKey.pending(rid.value, 1)],
        graded_at=datetime.now(UTC),
    )


def _disposition(rid: ReturnId) -> DispositionDecision:
    mrp = Money.of(Decimal("10000.00"))
    return DispositionDecision(
        return_id=rid,
        route=Route.RESELL,
        grade=Grade.A,
        mrp=mrp,
        recovery_value=mrp.percentage(75.0),
        liquidation_baseline=mrp.percentage(5.0),
        route_reason="test",
        fraud_flagged=False,
        decided_at=datetime.now(UTC),
    )


def _fraud(rid: ReturnId) -> FraudAssessment:
    return FraudAssessment.create(
        return_id=rid,
        buyer_id="buyer",
        sku_id="SKU",
        signals=[FraudSignal(name="S", weight=0, triggered=False, detail="ok")],
    )


@pytest.mark.asyncio
async def test_generate_health_card_success() -> None:
    rid = ReturnId.generate()
    grades = FakeConditionGradeRepository()
    dispositions = FakeDispositionRepository()
    fraud = FakeFraudRepository()
    hc_repo = FakeHealthCardRepository()
    qr_storage = FakeQRCodeStoragePort()
    qr_service = QRCodeGenerationService(base_url="https://returniq.example.com")
    await grades.save(_grade(rid))
    await dispositions.save(_disposition(rid))
    await fraud.save(_fraud(rid))

    uc = GenerateHealthCardUseCase(
        condition_grade_repository=grades,
        disposition_repository=dispositions,
        fraud_repository=fraud,
        health_card_repository=hc_repo,
        qr_storage_port=qr_storage,
        qr_generation_service=qr_service,
    )
    result = await uc.execute(rid.value)
    assert result.return_id == rid.value
    assert result.route == "RESELL"
    assert "verify" in result.verification_url
    assert qr_storage.has_image(f"health-cards/{rid.value}/qr.png")


@pytest.mark.asyncio
async def test_generate_raises_when_no_grade() -> None:
    rid = ReturnId.generate()
    uc = GenerateHealthCardUseCase(
        condition_grade_repository=FakeConditionGradeRepository(),
        disposition_repository=FakeDispositionRepository(),
        fraud_repository=FakeFraudRepository(),
        health_card_repository=FakeHealthCardRepository(),
        qr_storage_port=FakeQRCodeStoragePort(),
        qr_generation_service=QRCodeGenerationService(base_url="http://x"),
    )
    with pytest.raises(EntityNotFoundError):
        await uc.execute(rid.value)


@pytest.mark.asyncio
async def test_get_health_card_success() -> None:
    rid = ReturnId.generate()
    grades = FakeConditionGradeRepository()
    dispositions = FakeDispositionRepository()
    fraud = FakeFraudRepository()
    hc_repo = FakeHealthCardRepository()
    qr_storage = FakeQRCodeStoragePort()
    qr_service = QRCodeGenerationService(base_url="https://returniq.example.com")
    await grades.save(_grade(rid))
    await dispositions.save(_disposition(rid))
    await fraud.save(_fraud(rid))
    gen_uc = GenerateHealthCardUseCase(
        condition_grade_repository=grades,
        disposition_repository=dispositions,
        fraud_repository=fraud,
        health_card_repository=hc_repo,
        qr_storage_port=qr_storage,
        qr_generation_service=qr_service,
    )
    await gen_uc.execute(rid.value)

    get_uc = GetHealthCardUseCase(health_card_repository=hc_repo)
    result = await get_uc.execute(rid.value)
    assert result.return_id == rid.value
    assert result.grade == "A"


@pytest.mark.asyncio
async def test_get_health_card_not_found() -> None:
    uc = GetHealthCardUseCase(health_card_repository=FakeHealthCardRepository())
    with pytest.raises(EntityNotFoundError):
        await uc.execute("NOTEXIST")


@pytest.mark.asyncio
async def test_get_by_qr_success() -> None:
    rid = ReturnId.generate()
    grades = FakeConditionGradeRepository()
    dispositions = FakeDispositionRepository()
    fraud = FakeFraudRepository()
    hc_repo = FakeHealthCardRepository()
    qr_storage = FakeQRCodeStoragePort()
    qr_service = QRCodeGenerationService(base_url="https://returniq.example.com")
    await grades.save(_grade(rid))
    await dispositions.save(_disposition(rid))
    await fraud.save(_fraud(rid))
    gen_uc = GenerateHealthCardUseCase(
        condition_grade_repository=grades,
        disposition_repository=dispositions,
        fraud_repository=fraud,
        health_card_repository=hc_repo,
        qr_storage_port=qr_storage,
        qr_generation_service=qr_service,
    )
    gen_result = await gen_uc.execute(rid.value)

    by_qr_uc = GetHealthCardByQRUseCase(health_card_repository=hc_repo)
    result = await by_qr_uc.execute(gen_result.qr_token)
    assert result.return_id == rid.value


@pytest.mark.asyncio
async def test_get_by_qr_not_found() -> None:
    uc = GetHealthCardByQRUseCase(health_card_repository=FakeHealthCardRepository())
    with pytest.raises(QRTokenNotFoundError):
        await uc.execute("nonexistent_token")
