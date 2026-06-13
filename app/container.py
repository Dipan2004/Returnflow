# app/container.py
from __future__ import annotations

from dependency_injector import containers, providers

from app.application.use_cases.complete_image_upload_use_case import (
    CompleteImageUploadUseCase,
)
from app.application.use_cases.create_return_use_case import CreateReturnUseCase
from app.application.use_cases.get_condition_grade_use_case import GetConditionGradeUseCase
from app.application.use_cases.get_return_status_use_case import GetReturnStatusUseCase
from app.application.use_cases.get_return_use_case import GetReturnUseCase
from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.config import AppConfig, get_config
from app.domain.services.human_review_decision import ConfidenceGate
from app.infrastructure.adapters.grading.rekognition_adapter import RekognitionGradingAdapter
from app.infrastructure.aws.clients import (
    build_dynamodb_table,
    build_rekognition_client,
    build_s3_client,
)
from app.infrastructure.persistence.dynamodb_condition_grade_repository import (
    DynamoDBConditionGradeRepository,
)
from app.infrastructure.persistence.dynamodb_return_repository import (
    DynamoDBReturnRepository,
)
from app.infrastructure.storage.s3_image_storage import S3ImageStorage


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["app.api.routers"],
    )

    config: providers.Singleton[AppConfig] = providers.Singleton(get_config)

    dynamodb_table = providers.Singleton(build_dynamodb_table, config=config)

    s3_client = providers.Singleton(build_s3_client, config=config)

    rekognition_client = providers.Singleton(build_rekognition_client, config=config)

    return_repository = providers.Singleton(
        DynamoDBReturnRepository,
        table=dynamodb_table,
    )

    condition_grade_repository = providers.Singleton(
        DynamoDBConditionGradeRepository,
        table=dynamodb_table,
    )

    image_storage = providers.Singleton(
        S3ImageStorage,
        client=s3_client,
        bucket=config.provided.s3_image_bucket,
        upload_expiry_seconds=config.provided.s3_presign_expiry_seconds,
    )

    grading_adapter = providers.Singleton(
        RekognitionGradingAdapter,
        rekognition_client=rekognition_client,
        max_labels=config.provided.rekognition_max_labels,
        min_confidence=config.provided.rekognition_min_confidence,
    )

    confidence_gate = providers.Singleton(
        ConfidenceGate,
        threshold=config.provided.grading_confidence_threshold,
    )

    create_return_use_case = providers.Factory(
        CreateReturnUseCase,
        return_repository=return_repository,
        image_storage=image_storage,
    )

    get_return_use_case = providers.Factory(
        GetReturnUseCase,
        return_repository=return_repository,
    )

    get_return_status_use_case = providers.Factory(
        GetReturnStatusUseCase,
        return_repository=return_repository,
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

    get_condition_grade_use_case = providers.Factory(
        GetConditionGradeUseCase,
        condition_grade_repository=condition_grade_repository,
    )