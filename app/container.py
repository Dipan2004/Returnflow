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
from app.application.use_cases.get_dashboard_metrics_use_case import GetDashboardMetricsUseCase
from app.application.use_cases.get_disposition_use_case import GetDispositionUseCase
from app.application.use_cases.get_fraud_assessment_use_case import GetFraudAssessmentUseCase
from app.application.use_cases.get_health_card_by_qr_use_case import GetHealthCardByQRUseCase
from app.application.use_cases.get_health_card_use_case import GetHealthCardUseCase
from app.application.use_cases.get_outcome_use_case import GetOutcomeUseCase
from app.application.use_cases.get_return_status_use_case import GetReturnStatusUseCase
from app.application.use_cases.get_return_use_case import GetReturnUseCase
from app.application.use_cases.get_review_status_use_case import GetReviewStatusUseCase
from app.application.use_cases.get_size_recommendation_use_case import (
    GetSizeRecommendationUseCase,
)
from app.application.use_cases.get_verification_history_use_case import (
    GetVerificationHistoryUseCase,
)
from app.application.use_cases.get_workflow_state_use_case import GetWorkflowStateUseCase
from app.application.use_cases.match_buyer_use_case import MatchBuyerUseCase
from app.application.use_cases.orchestrate_disposition_use_case import (
    OrchestrateDispositionUseCase,
)
from app.application.use_cases.predict_return_use_case import PredictReturnUseCase
from app.application.use_cases.process_grading_use_case import ProcessGradingUseCase
from app.application.use_cases.reject_buyer_match_use_case import RejectBuyerMatchUseCase
from app.application.use_cases.verify_qr_token_use_case import VerifyQrTokenUseCase
from app.config import AppConfig, get_config
from app.domain.services.buyer_matching_engine import BuyerMatchingEngine
from app.domain.services.dashboard_aggregation_engine import DashboardAggregationEngine
from app.domain.services.disposition_engine import DispositionEngine
from app.domain.services.disposition_orchestrator import DispositionOrchestrator
from app.domain.services.fraud_engine import FraudEngine
from app.domain.services.human_review_decision import ConfidenceGate
from app.domain.services.prevent_iq_engine import PreventIQEngine
from app.domain.services.qr_generation_service import QRCodeGenerationService
from app.infrastructure.adapters.bedrock.bedrock_description_adapter import (
    BedrockDescriptionAdapter,
)
from app.infrastructure.adapters.bedrock.stub_description_adapter import StubDescriptionAdapter
from app.infrastructure.adapters.buyer_match.in_memory_buyer_matching_adapter import (
    InMemoryBuyerMatchingAdapter,
)
from app.infrastructure.adapters.buyer_match.in_memory_demand_index import InMemoryDemandIndex
from app.infrastructure.adapters.catalog.in_memory_product_catalog import (
    InMemoryProductCatalog,
)
from app.infrastructure.adapters.demand.in_memory_demand_signal import InMemoryDemandSignal
from app.infrastructure.adapters.features.in_memory_buyer_features import InMemoryBuyerFeatures
from app.infrastructure.adapters.features.in_memory_sku_features import InMemorySkuFeatures
from app.infrastructure.adapters.fraud.dynamodb_fraud_history_adapter import (
    DynamoDBFraudHistoryAdapter,
)
from app.infrastructure.adapters.fraud.in_memory_fraud_history_adapter import (
    InMemoryFraudHistoryAdapter,
)
from app.infrastructure.adapters.grading.demo_grading_adapter import DemoGradingAdapter
from app.infrastructure.adapters.grading.rekognition_adapter import RekognitionGradingAdapter
from app.infrastructure.adapters.notifications.local_notification_adapter import (
    LocalNotificationAdapter,
)
from app.infrastructure.adapters.prediction.demo_prediction_model import DemoPredictionModel
from app.infrastructure.adapters.qr_storage.local_qr_storage import LocalQRCodeStorage
from app.infrastructure.adapters.sqs.sqs_human_review_adapter import SQSHumanReviewAdapter
from app.infrastructure.adapters.sqs.stub_human_review_adapter import StubHumanReviewAdapter
from app.infrastructure.adapters.storage.stub_image_storage import StubImageStorage
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
from app.infrastructure.persistence.dynamodb_dashboard_repository import (
    DynamoDBDashboardRepository,
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
from app.infrastructure.persistence.in_memory_buyer_match_repository import (
    InMemoryBuyerMatchRepository,
)
from app.infrastructure.persistence.in_memory_condition_grade_repository import (
    InMemoryConditionGradeRepository,
)
from app.infrastructure.persistence.in_memory_dashboard_repository import (
    InMemoryDashboardRepository,
)
from app.infrastructure.persistence.in_memory_disposition_repository import (
    InMemoryDispositionRepository,
)
from app.infrastructure.persistence.in_memory_fraud_repository import InMemoryFraudRepository
from app.infrastructure.persistence.in_memory_health_card_repository import (
    InMemoryHealthCardRepository,
)
from app.infrastructure.persistence.in_memory_outcome_repository import (
    InMemoryOutcomeRepository,
)
from app.infrastructure.persistence.in_memory_return_repository import InMemoryReturnRepository
from app.infrastructure.persistence.in_memory_verification_audit_repository import (
    InMemoryVerificationAuditRepository,
)
from app.infrastructure.persistence.in_memory_workflow_state_repository import (
    InMemoryWorkflowStateRepository,
)
from app.infrastructure.storage.s3_image_storage import S3ImageStorage


def _build_return_repository(table):
    if table is None:
        return InMemoryReturnRepository()
    return DynamoDBReturnRepository(table=table)


def _build_condition_grade_repository(table):
    if table is None:
        return InMemoryConditionGradeRepository()
    return DynamoDBConditionGradeRepository(table=table)


def _build_workflow_state_repository(table):
    if table is None:
        return InMemoryWorkflowStateRepository()
    return DynamoDBWorkflowStateRepository(table=table)


def _build_disposition_repository(table):
    if table is None:
        return InMemoryDispositionRepository()
    return DynamoDBDispositionRepository(table=table)


def _build_fraud_repository(table):
    if table is None:
        return InMemoryFraudRepository()
    return DynamoDBFraudRepository(table=table)


def _build_buyer_match_repository(table):
    if table is None:
        return InMemoryBuyerMatchRepository()
    return DynamoDBBuyerMatchRepository(table=table)


def _build_health_card_repository(table):
    if table is None:
        return InMemoryHealthCardRepository()
    return DynamoDBHealthCardRepository(table=table)


def _build_verification_audit_repository(table):
    if table is None:
        return InMemoryVerificationAuditRepository()
    return DynamoDBVerificationAuditRepository(table=table)


def _build_outcome_repository(table):
    if table is None:
        return InMemoryOutcomeRepository()
    return DynamoDBOutcomeRepository(table=table)


def _build_dashboard_repository(table):
    if table is None:
        return InMemoryDashboardRepository()
    return DynamoDBDashboardRepository(table=table)


def _build_fraud_history_port(table):
    if table is None:
        return InMemoryFraudHistoryAdapter()
    return DynamoDBFraudHistoryAdapter(table=table)


def _build_image_storage(s3_client, bucket, upload_expiry_seconds):
    if s3_client is None:
        return StubImageStorage()
    return S3ImageStorage(
        client=s3_client,
        bucket=bucket,
        upload_expiry_seconds=upload_expiry_seconds,
    )


def _build_description_adapter(bedrock_client, model_id):
    if bedrock_client is None:
        return StubDescriptionAdapter()
    return BedrockDescriptionAdapter(bedrock_client=bedrock_client, model_id=model_id)


def _build_grading_adapter(rekognition_client, description_port, max_labels, min_confidence):
    if rekognition_client is None:
        return DemoGradingAdapter()
    return RekognitionGradingAdapter(
        rekognition_client=rekognition_client,
        description_port=description_port,
        max_labels=max_labels,
        min_confidence=min_confidence,
    )


def _build_human_review_queue(sqs_client, queue_url):
    if sqs_client is None:
        return StubHumanReviewAdapter()
    return SQSHumanReviewAdapter(sqs_client=sqs_client, queue_url=queue_url)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.api.routers"])

    config: providers.Singleton[AppConfig] = providers.Singleton(get_config)

    dynamodb_table = providers.Singleton(build_dynamodb_table, config=config)
    s3_client = providers.Singleton(build_s3_client, config=config)
    rekognition_client = providers.Singleton(build_rekognition_client, config=config)
    bedrock_client = providers.Singleton(build_bedrock_client, config=config)
    sqs_client = providers.Singleton(build_sqs_client, config=config)

    return_repository = providers.Singleton(_build_return_repository, table=dynamodb_table)
    condition_grade_repository = providers.Singleton(
        _build_condition_grade_repository, table=dynamodb_table
    )
    workflow_state_repository = providers.Singleton(
        _build_workflow_state_repository, table=dynamodb_table
    )
    disposition_repository = providers.Singleton(
        _build_disposition_repository, table=dynamodb_table
    )
    fraud_repository = providers.Singleton(_build_fraud_repository, table=dynamodb_table)

    image_storage = providers.Singleton(
        _build_image_storage,
        s3_client=s3_client,
        bucket=config.provided.s3_image_bucket,
        upload_expiry_seconds=config.provided.s3_presign_expiry_seconds,
    )

    description_adapter = providers.Singleton(
        _build_description_adapter,
        bedrock_client=bedrock_client,
        model_id=config.provided.bedrock_model_id,
    )

    grading_adapter = providers.Singleton(
        _build_grading_adapter,
        rekognition_client=rekognition_client,
        description_port=description_adapter,
        max_labels=config.provided.rekognition_max_labels,
        min_confidence=config.provided.rekognition_min_confidence,
    )

    human_review_queue = providers.Singleton(
        _build_human_review_queue,
        sqs_client=sqs_client,
        queue_url=config.provided.sqs_human_review_queue_url,
    )

    demand_signal_port = providers.Singleton(InMemoryDemandSignal)
    product_catalog_port = providers.Singleton(InMemoryProductCatalog)
    fraud_history_port = providers.Singleton(_build_fraud_history_port, table=dynamodb_table)

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
    buyer_match_repository = providers.Singleton(
        _build_buyer_match_repository, table=dynamodb_table
    )
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

    health_card_repository = providers.Singleton(
        _build_health_card_repository, table=dynamodb_table
    )

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
        _build_verification_audit_repository, table=dynamodb_table
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

    outcome_repository = providers.Singleton(_build_outcome_repository, table=dynamodb_table)
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

    buyer_feature_port = providers.Singleton(InMemoryBuyerFeatures)
    sku_feature_port = providers.Singleton(InMemorySkuFeatures)
    prediction_model = providers.Singleton(DemoPredictionModel)
    prevent_iq_engine = providers.Singleton(PreventIQEngine)

    predict_return_use_case = providers.Factory(
        PredictReturnUseCase,
        buyer_feature_port=buyer_feature_port,
        sku_feature_port=sku_feature_port,
        prediction_model=prediction_model,
        prevent_iq_engine=prevent_iq_engine,
    )
    get_size_recommendation_use_case = providers.Factory(
        GetSizeRecommendationUseCase,
        sku_feature_port=sku_feature_port,
        prevent_iq_engine=prevent_iq_engine,
    )

    dashboard_repository = providers.Singleton(_build_dashboard_repository, table=dynamodb_table)
    dashboard_aggregation_engine = providers.Singleton(DashboardAggregationEngine)

    get_dashboard_metrics_use_case = providers.Factory(
        GetDashboardMetricsUseCase,
        dashboard_repository=dashboard_repository,
        aggregation_engine=dashboard_aggregation_engine,
    )
