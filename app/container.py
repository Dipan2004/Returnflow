# app/container.py
from __future__ import annotations

from dependency_injector import containers, providers

from app.application.services.grading_workflow_service import GradingWorkflowService
from app.application.use_cases.accept_buyer_match_use_case import AcceptBuyerMatchUseCase
from app.application.use_cases.assess_fraud_use_case import AssessFraudUseCase
from app.application.use_cases.calculate_disposition_use_case import (
    CalculateDispositionUseCase,
)
from app.application.use_cases.complete_image_upload_use_case import CompleteImageUploadUseCase
from app.application.use_cases.create_outcome_use_case import CreateOutcomeUseCase
from app.application.use_cases.create_return_use_case import CreateReturnUseCase
from app.application.use_cases.generate_health_card_use_case import GenerateHealthCardUseCase
from app.application.use_cases.get_buyer_match_use_case import GetBuyerMatchUseCase
from app.application.use_cases.get_condition_grade_use_case import GetConditionGradeUseCase
from app.application.use_cases.get_disposition_use_case import GetDispositionUseCase
from app.application.use_cases.get_fraud_assessment_use_case import GetFraudAssessmentUseCase
from app.application.use_cases.get_health_card_by_qr_use_case import GetHealthCardByQRUseCase
from app.application.use_cases.get_health_card_use_case import GetHealthCardUseCase
from app.application.use_cases.get_outcome_use_case import GetOutcomeUseCase
from app.application.use_cases.get_return_status_use_case import GetReturnStatusUseCase
from app.application.use_cases.get_return_use_case import GetReturnUseCase
from app.application.use_cases.get_review_status_use_case import GetReviewStatusUseCase
from app.application.use_cases.get_verification_history_use_case import (
    GetVerificationHistoryUseCase,
)
from app.application.use_cases.get_workflow_state_use_case import GetWorkflowStateUseCase
from app.application.use_cases.match_buyer_use_case import MatchBuyerUseCase
from app.application.use_cases.orchestrate_disposition_use_case import (
    OrchestrateDispositionUseCase,
)
from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.application.use_cases.reject_buyer_match_use_case import RejectBuyerMatchUseCase
from app.application.use_cases.verify_qr_token_use_case import VerifyQrTokenUseCase
from app.config import AppConfig, get_config
from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
from app.domain.services.disposition_engine import DispositionEngine
from app.domain.services.disposition_orchestrator import DispositionOrchestrator
from app.domain.services.fraud_engine import FraudEngine
from app.domain.services.human_review_decision import ConfidenceGate
from app.domain.services.qr_generation_service import QRCodeGenerationService
from app.infrastructure.adapters.bedrock.bedrock_description_adapter import (
    BedrockDescriptionAdapter,
)
from app.infrastructure.adapters.buyer_match.in_memory_buyer_matching_adapter import (
    InMemoryBuyerMatchingAdapter,
)
from app.infrastructure.adapters.buyer_match.in_memory_demand_index import InMemoryDemandIndex
from app.infrastructure.adapters.catalog.in_memory_product_catalog import (
    InMemoryProductCatalog,
)
from app.infrastructure.adapters.demand.in_memory_demand_signal import InMemoryDemandSignal
from app.infrastructure.adapters.fraud.dynamodb_fraud_history_adapter import (
    DynamoDBFraudHistoryAdapter,
)
from app.infrastructure.adapters.grading.rekognition_adapter import RekognitionGradingAdapter
from app.infrastructure.adapters.notifications.local_notification_adapter import (
    LocalNotificationAdapter,
)
from app.infrastructure.adapters.qr_storage.local_qr_storage import LocalQRCodeStorage
from app.infrastructure.adapters.sqs.sqs_human_review_adapter import SQSHumanReviewAdapter
from app.infrastructure.aws.clients import (
    build_bedrock_client,
    build_dynamodb_table,
    build_rekognition_client,
    build_s3_client,
    build_sqs_client,
)
from app.infrastructure.persistence.dynamodb_buyer_match_repository import (
    DynamoDBBuyerMatchRepository,
)
from app.infrastructure.persistence.dynamodb_condition_grade_repository import (
    DynamoDBConditionGradeRepository,
)
from app.infrastructure.persistence.dynamodb_disposition_repository import (
    DynamoDBDispositionRepository,
)
from app.infrastructure.persistence.dynamodb_fraud_repository import DynamoDBFraudRepository
from app.infrastructure.persistence.dynamodb_health_card_repository import (
    DynamoDBHealthCardRepository,
)
from app.infrastructure.persistence.dynamodb_outcome_repository import (
    DynamoDBOutcomeRepository,
)
from app.infrastructure.persistence.dynamodb_return_repository import DynamoDBReturnRepository
from app.infrastructure.persistence.dynamodb_verification_audit_repository import (
    DynamoDBVerificationAuditRepository,
)
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
    disposition_repository = providers.Singleton(
        DynamoDBDispositionRepository, table=dynamodb_table
    )
    fraud_repository = providers.Singleton(DynamoDBFraudRepository, table=dynamodb_table)
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

    demand_signal_port = providers.Singleton(InMemoryDemandSignal)
    product_catalog_port = providers.Singleton(InMemoryProductCatalog)
    fraud_history_port = providers.Singleton(DynamoDBFraudHistoryAdapter, table=dynamodb_table)

    confidence_gate = providers.Singleton(
        ConfidenceGate, threshold=config.provided.grading_confidence_threshold
    )

    disposition_engine = providers.Singleton(
        DispositionEngine,
        p2p_max_radius_km=config.provided.p2p_max_radius_km,
    )

    fraud_engine = providers.Singleton(
        FraudEngine,
        bulk_buy_threshold=config.provided.fraud_bulk_buy_threshold,
        window_hours=config.provided.fraud_window_hours,
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
    calculate_disposition_use_case = providers.Factory(
        CalculateDispositionUseCase,
        return_repository=return_repository,
        condition_grade_repository=condition_grade_repository,
        disposition_repository=disposition_repository,
        demand_signal_port=demand_signal_port,
        product_catalog_port=product_catalog_port,
        disposition_engine=disposition_engine,
        fraud_history_port=fraud_history_port,
        fraud_repository=fraud_repository,
        fraud_engine=fraud_engine,
    )
    get_disposition_use_case = providers.Factory(
        GetDispositionUseCase,
        disposition_repository=disposition_repository,
    )
    assess_fraud_use_case = providers.Factory(
        AssessFraudUseCase,
        fraud_history_port=fraud_history_port,
        fraud_repository=fraud_repository,
        fraud_engine=fraud_engine,
    )
    get_fraud_assessment_use_case = providers.Factory(
        GetFraudAssessmentUseCase,
        fraud_repository=fraud_repository,
    )

    demand_index_port = providers.Singleton(InMemoryDemandIndex)
    buyer_matching_port = providers.Singleton(InMemoryBuyerMatchingAdapter)
    buyer_match_repository = providers.Singleton(DynamoDBBuyerMatchRepository, table=dynamodb_table)
    buyer_matching_engine = providers.Singleton(BuyerMatchingEngine)

    match_buyer_use_case = providers.Factory(
        MatchBuyerUseCase,
        demand_index_port=demand_index_port,
        buyer_matching_port=buyer_matching_port,
        buyer_match_repository=buyer_match_repository,
        buyer_matching_engine=buyer_matching_engine,
    )
    get_buyer_match_use_case = providers.Factory(
        GetBuyerMatchUseCase,
        buyer_match_repository=buyer_match_repository,
    )

    disposition_orchestrator = providers.Singleton(
        DispositionOrchestrator,
        p2p_max_radius_km=config.provided.p2p_max_radius_km,
    )

    orchestrate_disposition_use_case = providers.Factory(
        OrchestrateDispositionUseCase,
        return_repository=return_repository,
        condition_grade_repository=condition_grade_repository,
        fraud_repository=fraud_repository,
        buyer_match_repository=buyer_match_repository,
        disposition_repository=disposition_repository,
        product_catalog_port=product_catalog_port,
        orchestrator=disposition_orchestrator,
    )

    health_card_repository = providers.Singleton(DynamoDBHealthCardRepository, table=dynamodb_table)

    qr_storage_port = providers.Singleton(LocalQRCodeStorage, base_url=config.provided.base_url)

    qr_generation_service = providers.Singleton(
        QRCodeGenerationService,
        base_url=config.provided.base_url,
        ttl_hours=config.provided.qr_token_ttl_hours,
    )

    generate_health_card_use_case = providers.Factory(
        GenerateHealthCardUseCase,
        condition_grade_repository=condition_grade_repository,
        disposition_repository=disposition_repository,
        fraud_repository=fraud_repository,
        health_card_repository=health_card_repository,
        qr_storage_port=qr_storage_port,
        qr_generation_service=qr_generation_service,
    )

    get_health_card_use_case = providers.Factory(
        GetHealthCardUseCase,
        health_card_repository=health_card_repository,
    )

    get_health_card_by_qr_use_case = providers.Factory(
        GetHealthCardByQRUseCase,
        health_card_repository=health_card_repository,
    )

    verification_audit_repository = providers.Singleton(
        DynamoDBVerificationAuditRepository, table=dynamodb_table
    )

    verify_qr_token_use_case = providers.Factory(
        VerifyQrTokenUseCase,
        health_card_repository=health_card_repository,
        verification_audit_repository=verification_audit_repository,
    )

    get_verification_history_use_case = providers.Factory(
        GetVerificationHistoryUseCase,
        verification_audit_repository=verification_audit_repository,
    )

    outcome_repository = providers.Singleton(DynamoDBOutcomeRepository, table=dynamodb_table)
    notification_port = providers.Singleton(LocalNotificationAdapter)

    create_outcome_use_case = providers.Factory(
        CreateOutcomeUseCase,
        outcome_repository=outcome_repository,
    )
    accept_buyer_match_use_case = providers.Factory(
        AcceptBuyerMatchUseCase,
        outcome_repository=outcome_repository,
        health_card_repository=health_card_repository,
    )
    reject_buyer_match_use_case = providers.Factory(
        RejectBuyerMatchUseCase,
        outcome_repository=outcome_repository,
        health_card_repository=health_card_repository,
    )
    get_outcome_use_case = providers.Factory(
        GetOutcomeUseCase,
        outcome_repository=outcome_repository,
    )
