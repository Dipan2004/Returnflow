# app/application/use_cases/process_grading_use_case.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.grading_port import GradingPort
from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.dto import DamageLabelDTO, ProcessGradingResult
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.exceptions import EntityNotFoundError
from app.domain.services.human_review_decision import ConfidenceGate
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class ProcessGradingUseCase:
    def __init__(
        self,
        grading_port: GradingPort,
        condition_grade_repository: ConditionGradeRepository,
        return_repository: ReturnRepository,
        confidence_gate: ConfidenceGate,
        image_bucket: str,
    ) -> None:
        self._grading_port = grading_port
        self._grade_repository = condition_grade_repository
        self._return_repository = return_repository
        self._confidence_gate = confidence_gate
        self._image_bucket = image_bucket

    async def execute(self, return_id_str: str) -> ProcessGradingResult:
        return_id = ReturnId(return_id_str)
        return_request = await self._return_repository.get_by_id(return_id)
        if return_request is None:
            raise EntityNotFoundError("ReturnRequest", return_id_str)

        image_keys_str = [k.value for k in return_request.image_keys]

        logger.info(
            "Starting grading",
            return_id=return_id_str,
            image_count=len(image_keys_str),
        )

        grading_result = await self._grading_port.grade_images(
            bucket=self._image_bucket,
            image_keys=image_keys_str,
        )

        description_result = await self._grading_port.describe_damage(
            grade=grading_result.grade,
            damage_labels=grading_result.damage_labels,
        )

        image_keys = [ImageKey(k) for k in image_keys_str]

        condition_grade = ConditionGrade.create(
            return_id=return_id,
            grade=grading_result.grade,
            confidence=grading_result.confidence,
            damage_labels=grading_result.damage_labels,
            damage_description=description_result.description,
            image_keys=image_keys,
        )

        decision = self._confidence_gate.evaluate(condition_grade)

        if decision.requires_review:
            condition_grade = ConditionGrade.create_for_human_review(
                return_id=return_id,
                confidence=grading_result.confidence,
                damage_labels=grading_result.damage_labels,
                image_keys=image_keys,
            )
            logger.warning(
                "Routing to human review",
                return_id=return_id_str,
                confidence=grading_result.confidence,
                reason=decision.reason,
            )

        await self._grade_repository.save(condition_grade)

        logger.info(
            "Grading complete",
            return_id=return_id_str,
            grade=condition_grade.grade.value,
            confidence=condition_grade.confidence.value,
            human_review=condition_grade.routed_to_human_review,
        )

        return ProcessGradingResult(
            return_id=return_id_str,
            grade=condition_grade.grade.value,
            confidence=condition_grade.confidence.value,
            damage_labels=[
                DamageLabelDTO(name=d.name, confidence=d.confidence)
                for d in condition_grade.damage_labels
            ],
            damage_description=condition_grade.damage_description,
            routed_to_human_review=condition_grade.routed_to_human_review,
            graded_at=condition_grade.graded_at,
        )