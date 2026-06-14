# app/application/services/grading_workflow_service.py
from __future__ import annotations

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.application.ports.grading_port import GradingPort
from app.application.ports.human_review_queue_port import HumanReviewQueuePort
from app.application.ports.return_repository import ReturnRepository
from app.application.ports.workflow_state_repository import WorkflowStateRepository
from app.application.use_cases.dto import DamageLabelDTO, ProcessGradingResult
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.entities.human_review_request import HumanReviewRequest
from app.domain.entities.workflow_state import WorkflowState, WorkflowStep
from app.domain.exceptions import EntityNotFoundError
from app.domain.services.human_review_decision import ConfidenceGate
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GradingWorkflowService:
    def __init__(
        self,
        grading_port: GradingPort,
        condition_grade_repository: ConditionGradeRepository,
        return_repository: ReturnRepository,
        workflow_state_repository: WorkflowStateRepository,
        human_review_queue: HumanReviewQueuePort,
        confidence_gate: ConfidenceGate,
        image_bucket: str,
    ) -> None:
        self._grading_port = grading_port
        self._grade_repository = condition_grade_repository
        self._return_repository = return_repository
        self._workflow_repository = workflow_state_repository
        self._review_queue = human_review_queue
        self._confidence_gate = confidence_gate
        self._image_bucket = image_bucket

    async def execute(self, return_id_str: str) -> ProcessGradingResult:
        return_id = ReturnId(return_id_str)
        return_request = await self._return_repository.get_by_id(return_id)
        if return_request is None:
            raise EntityNotFoundError("ReturnRequest", return_id_str)

        image_keys_str = [k.value for k in return_request.image_keys]
        workflow = WorkflowState.create(return_id)

        logger.info(
            "Grading workflow started",
            return_id=return_id_str,
            image_count=len(image_keys_str),
        )

        workflow.record_step_start(WorkflowStep.GRADE_IMAGES)
        try:
            grading_result = await self._grading_port.grade_images(
                bucket=self._image_bucket,
                image_keys=image_keys_str,
            )
        except Exception as exc:
            workflow.record_step_failed(WorkflowStep.GRADE_IMAGES, str(exc))
            await self._workflow_repository.save(workflow)
            raise

        workflow.record_step_complete(
            WorkflowStep.GRADE_IMAGES,
            metadata={
                "grade": grading_result.grade.value,
                "confidence": grading_result.confidence,
                "raw_label_count": grading_result.raw_label_count,
            },
        )

        workflow.record_step_start(WorkflowStep.CHECK_CONFIDENCE)
        image_keys = [ImageKey(k) for k in image_keys_str]

        condition_grade = ConditionGrade.create(
            return_id=return_id,
            grade=grading_result.grade,
            confidence=grading_result.confidence,
            damage_labels=grading_result.damage_labels,
            damage_description=grading_result.damage_description,
            image_keys=image_keys,
        )

        decision = self._confidence_gate.evaluate(condition_grade)
        workflow.record_step_complete(
            WorkflowStep.CHECK_CONFIDENCE,
            metadata={
                "confidence": grading_result.confidence,
                "threshold": self._confidence_gate.threshold,
                "requires_review": decision.requires_review,
            },
        )

        if decision.requires_review:
            workflow.record_step_start(WorkflowStep.SEND_TO_HUMAN_REVIEW)
            condition_grade = ConditionGrade.create_for_human_review(
                return_id=return_id,
                confidence=grading_result.confidence,
                damage_labels=grading_result.damage_labels,
                image_keys=image_keys,
            )

            review_request = HumanReviewRequest.create(
                return_id=return_id,
                confidence=grading_result.confidence,
                threshold=self._confidence_gate.threshold,
                damage_labels=grading_result.damage_labels,
                image_keys=image_keys,
                reason=decision.reason,
            )

            try:
                publish_result = await self._review_queue.publish(review_request)
                workflow.record_step_complete(
                    WorkflowStep.SEND_TO_HUMAN_REVIEW,
                    metadata={"message_id": publish_result.message_id},
                )
            except Exception as exc:
                workflow.record_step_failed(WorkflowStep.SEND_TO_HUMAN_REVIEW, str(exc))
                await self._workflow_repository.save(workflow)
                raise

            workflow.mark_sent_to_review()
            await self._grade_repository.save(condition_grade)
            await self._workflow_repository.save(workflow)

            logger.warning(
                "Grading routed to human review",
                return_id=return_id_str,
                confidence=grading_result.confidence,
                priority=review_request.priority.value,
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
                routed_to_human_review=True,
                graded_at=condition_grade.graded_at,
            )

        workflow.record_step_start(WorkflowStep.GENERATE_DAMAGE_DESCRIPTION)
        workflow.record_step_complete(
            WorkflowStep.GENERATE_DAMAGE_DESCRIPTION,
            metadata={
                "word_count": len(grading_result.damage_description.split()),
                "used_fallback": grading_result.description_used_fallback,
            },
        )

        workflow.mark_completed()
        await self._grade_repository.save(condition_grade)
        await self._workflow_repository.save(workflow)

        logger.info(
            "Grading workflow completed",
            return_id=return_id_str,
            grade=condition_grade.grade.value,
            confidence=condition_grade.confidence.value,
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
            routed_to_human_review=False,
            graded_at=condition_grade.graded_at,
        )
