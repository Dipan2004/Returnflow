# app/container.py
from __future__ import annotations

from dependency_injector import containers, providers

from app.application.services.grading_workflow_service import GradingWorkflowService
from app.application.use_cases.complete_image_upload_use_case import CompleteImageUploadUseCase
from app.application.use_cases.create_return_use_case import CreateReturnUseCase
from app.application.use_cases.get_condition_grade_use_case import GetConditionGradeUseCase
from app.application.use_cases.get_return_status_use_case import GetReturnStatusUseCase
from app.application.use_cases.get_return_use_case import GetReturnUseCase
from app.application.use_cases.get_review_status_use_case import GetReviewStatusUseCase
from app.application.use_cases.get_workflow_state_use_case import GetWorkflowStateUseCase
from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.config import AppConfig, get_config
from app.domain.services.human_review_decision import ConfidenceGate
from app.infrastructure.adapters.bedrock.bedrock_description_adapter import (
    BedrockDescriptionAdapter,
)
from app.infrastructure.adapters.grading.rekognition_adapter import RekognitionGradingAdapter
from app.infrastructure.adapters.sqs.sqs_human_review_adapter import SQSHumanReviewAdapter
from app.infrastructure.aws.clients import (
    build_bedrock_client,
    build_dynamodb_table,
    build_rekognition_client,
    build_s3_client,
    build_sqs_client,
)
from app.infrastructure.persistence.dynamodb_condition_grade_repository import (
    DynamoDBConditionGradeRepository,
)
from app.infrastructure.persistence.dynamodb_return_repository import DynamoDBReturnRepository
from app.infrastructure.persistence.dynamodb_workflow_state_repository import (
    DynamoDBWorkflowStateRepository,
)
from app.infrastructure.storage.s3_image_storage import S3ImageStorage


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.api.routers"])

    config: providers.Singleton[AppConfig] = providers.Singleton(get_config)

    dynamodb_table = providers.Singleton(build_dynamodb_table, config=config)
    s3_client = providers.Singleton(build_s3_client, config=config)
    rekognition_client = providers.Singleton(build_rekognition_client, config=config)
    bedrock_client = providers.Singleton(build_bedrock_client, config=config)
    sqs_client = providers.Singleton(build_sqs_client, config=config)

    return_repository = providers.Singleton(DynamoDBReturnRepository, table=dynamodb_table)
    condition_grade_repository = providers.Singleton(
        DynamoDBConditionGradeRepository, table=dynamodb_table
    )
    workflow_state_repository = providers.Singleton(
        DynamoDBWorkflowStateRepository, table=dynamodb_table
    )
    image_storage = providers.Singleton(
        S3ImageStorage,
        client=s3_client,
        bucket=config.provided.s3_image_bucket,
        upload_expiry_seconds=config.provided.s3_presign_expiry_seconds,
    )

    description_adapter = providers.Singleton(
        BedrockDescriptionAdapter,
        bedrock_client=bedrock_client,
        model_id=config.provided.bedrock_model_id,
    )

    grading_adapter = providers.Singleton(
        RekognitionGradingAdapter,
        rekognition_client=rekognition_client,
        description_port=description_adapter,
        max_labels=config.provided.rekognition_max_labels,
        min_confidence=config.provided.rekognition_min_confidence,
    )

    human_review_queue = providers.Singleton(
        SQSHumanReviewAdapter,
        sqs_client=sqs_client,
        queue_url=config.provided.sqs_human_review_queue_url,
    )

    confidence_gate = providers.Singleton(
        ConfidenceGate, threshold=config.provided.grading_confidence_threshold
    )

    create_return_use_case = providers.Factory(
        CreateReturnUseCase,
        return_repository=return_repository,
        image_storage=image_storage,
    )
    get_return_use_case = providers.Factory(GetReturnUseCase, return_repository=return_repository)
    get_return_status_use_case = providers.Factory(
        GetReturnStatusUseCase, return_repository=return_repository
    )
    complete_image_upload_use_case = providers.Factory(
        CompleteImageUploadUseCase,
        return_repository=return_repository,
        image_storage=image_storage,
    )
    process_grading_use_case = providers.Factory(
        ProcessGradingUseCase,
        grading_port=grading_adapter,
        condition_grade_repository=condition_grade_repository,
        return_repository=return_repository,
        confidence_gate=confidence_gate,
        image_bucket=config.provided.s3_image_bucket,
    )
    grading_workflow_service = providers.Factory(
        GradingWorkflowService,
        grading_port=grading_adapter,
        condition_grade_repository=condition_grade_repository,
        return_repository=return_repository,
        workflow_state_repository=workflow_state_repository,
        human_review_queue=human_review_queue,
        confidence_gate=confidence_gate,
        image_bucket=config.provided.s3_image_bucket,
    )
    get_condition_grade_use_case = providers.Factory(
        GetConditionGradeUseCase,
        condition_grade_repository=condition_grade_repository,
    )
    get_workflow_state_use_case = providers.Factory(
        GetWorkflowStateUseCase,
        workflow_state_repository=workflow_state_repository,
    )
    get_review_status_use_case = providers.Factory(
        GetReviewStatusUseCase,
        condition_grade_repository=condition_grade_repository,
        workflow_state_repository=workflow_state_repository,
    )
