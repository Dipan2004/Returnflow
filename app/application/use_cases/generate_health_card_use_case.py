# app/application/use_cases/generate_health_card_use_case.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.disposition_repository import DispositionRepository
from app.application.ports.fraud_repository import FraudRepository
from app.application.ports.health_card_repository import HealthCardRepository
from app.application.ports.qr_storage_port import QRCodeStoragePort
from app.application.use_cases.health_card_dto import GenerateHealthCardResult
from app.domain.entities.health_card import HealthCard
from app.domain.exceptions import EntityNotFoundError
from app.domain.services.qr_generation_service import QRCodeGenerationService
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GenerateHealthCardUseCase:
    def __init__(
        self,
        condition_grade_repository: ConditionGradeRepository,
        disposition_repository: DispositionRepository,
        fraud_repository: FraudRepository,
        health_card_repository: HealthCardRepository,
        qr_storage_port: QRCodeStoragePort,
        qr_generation_service: QRCodeGenerationService,
    ) -> None:
        self._grades = condition_grade_repository
        self._dispositions = disposition_repository
        self._fraud = fraud_repository
        self._health_cards = health_card_repository
        self._qr_storage = qr_storage_port
        self._qr_service = qr_generation_service

    async def execute(self, return_id_str: str) -> GenerateHealthCardResult:
        return_id = ReturnId(return_id_str)

        condition_grade = await self._grades.get_by_return_id(return_id)
        if condition_grade is None:
            raise EntityNotFoundError("ConditionGrade", return_id_str)

        disposition = await self._dispositions.get_by_return_id(return_id)
        if disposition is None:
            raise EntityNotFoundError("DispositionDecision", return_id_str)

        fraud_assessment = await self._fraud.get_by_return_id(return_id)

        qr_token = self._qr_service.generate_token(return_id)
        verification_url = self._qr_service.build_verification_url(qr_token.token)
        qr_image = self._qr_service.generate_qr_image(verification_url)
        storage_key = self._qr_service.build_storage_key(return_id)

        await self._qr_storage.store_qr_image(storage_key, qr_image)

        _fraud_risk = "UNKNOWN"
        if fraud_assessment is not None:
            _fraud_risk = fraud_assessment.risk_level.value

        health_card = HealthCard(
            return_id=return_id,
            sku_id=condition_grade.damage_description[:50] if not disposition else "SKU",
            grade=condition_grade.grade,
            confidence=condition_grade.confidence,
            damage_description=condition_grade.damage_description,
            route=disposition.route,
            mrp=disposition.mrp,
            recovery_value=disposition.recovery_value,
            value_delta=disposition.value_delta,
            image_keys=condition_grade.image_keys,
            qr_token=qr_token.token,
            qr_url=verification_url,
            created_at=qr_token.created_at,
            ttl_hours=qr_token.ttl_hours,
        )

        await self._health_cards.save(health_card)
        await self._health_cards.save_qr_token(qr_token)

        logger.info(
            "Health card generated",
            return_id=return_id_str,
            route=disposition.route.value,
            qr_token=qr_token.token[:8],
        )

        return GenerateHealthCardResult(
            return_id=return_id_str,
            qr_token=qr_token.token,
            verification_url=verification_url,
            route=disposition.route.value,
            condition_grade=condition_grade.grade.value,
            recovery_value=disposition.recovery_value.amount,
            created_at=health_card.created_at,
        )
