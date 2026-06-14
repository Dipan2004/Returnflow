# Repository Map

```
app/
  main.py                                 FastAPI app factory, exception
                                          handlers, lifespan/container wiring
  config.py                               AppConfig (pydantic-settings)
  container.py                            dependency-injector wiring

  domain/
    exceptions.py                         ReturnIQError hierarchy
    value_objects/
      return_id.py                        ULID-backed ReturnId
      image_key.py                        S3 key VO (pending/graded/...)
      grade.py                            Grade enum (A/B/C/DONATE/SCRAP)
      route.py                            Route enum (P2P/RESELL/...)
      confidence_score.py                 0-100 confidence VO
      money.py                            Decimal-backed INR money VO
    entities/
      return_request.py                   ReturnRequest aggregate (Phase 2)
      condition_grade.py                  Grading result entity (Phase 3A)
      human_review_request.py             Human review escalation (Phase 3Bb)
      workflow_state.py                   Workflow step tracking (Phase 3Bb)
      health_card.py                      Health Card aggregate (future)
      qr_token.py                         Tamper-evident QR token (future)
      buyer_match.py                      P2P buyer match (future)
      disposition_decision.py             Routing decision entity (Phase 4A)
      fraud_assessment.py                 Fraud check result (future)
    services/
      human_review_decision.py            ConfidenceGate service (Phase 3A)
      disposition_engine.py               DispositionEngine routing rules (Phase 4A)
    events/                               Domain events (return_submitted,
                                           grading_completed, disposition_routed)

  application/
    ports/
      return_repository.py                ReturnRepository (Phase 2 - impl)
      image_storage_port.py               ImageStoragePort (Phase 2 - impl)
      grading_port.py                     GradingPort (Phase 3A - impl)
      description_generation_port.py      DescriptionGenerationPort (Phase 3Ba - impl)
      condition_grade_repository.py       ConditionGradeRepository (Phase 3A - impl)
      human_review_queue_port.py          HumanReviewQueuePort (Phase 3Bb - impl)
      workflow_state_repository.py        WorkflowStateRepository (Phase 3Bb - impl)
      health_card_repository.py           HealthCardRepository (not yet impl.)
      notification_port.py                NotificationPort (not yet impl.)
      prediction_port.py                  PredictionPort (not yet impl.)
      fraud_port.py                       FraudPort (not yet impl.)
      demand_signal_port.py               DemandSignalPort (Phase 4A - stub)
      product_catalog_port.py             ProductCatalogPort (Phase 4A - stub)
      disposition_repository.py           DispositionRepository (Phase 4A - impl)
    services/
      grading_workflow_service.py         Full grading pipeline orchestration (Phase 3Bb)
    use_cases/
      dto.py                              Shared result DTOs
      disposition_dto.py                  Disposition request/response DTOs (Phase 4A)
      create_return_use_case.py           POST /returns
      get_return_use_case.py              GET /returns/{id}
      get_return_status_use_case.py       GET /returns/{id}/status
      complete_image_upload_use_case.py   POST /returns/{id}/images/complete
      process_grading_use_case.py         POST /grades (simple)
      get_condition_grade_use_case.py     GET /grades/{id}
      get_workflow_state_use_case.py      GET /grades/{id}/workflow
      get_review_status_use_case.py       GET /grades/{id}/review-status
      calculate_disposition_use_case.py   POST /dispositions/calculate (Phase 4A)
      get_disposition_use_case.py         GET /dispositions/{id} (Phase 4A)

  infrastructure/
    logging.py                            structlog configuration
    aws/clients.py                        boto3 DynamoDB/S3/Rekognition/
                                          Bedrock/SQS client factories
    adapters/
      grading/
        rekognition_adapter.py            RekognitionGradingAdapter (Phase 3A)
        grade_mapper.py                   Weighted damage → grade mapping
        models.py                         RawLabel, AggregatedLabelSet
      bedrock/
        bedrock_description_adapter.py    BedrockDescriptionAdapter (Phase 3Ba)
        prompt_templates.py               Deterministic prompt construction
        response_parser.py                Response validation + truncation
      sqs/
        sqs_human_review_adapter.py       SQSHumanReviewAdapter (Phase 3Bb)
    persistence/
      return_item_mapper.py               ReturnRequest <-> DynamoDB item
      dynamodb_return_repository.py       ReturnRepository impl.
      condition_grade_mapper.py           ConditionGrade <-> DynamoDB item
      dynamodb_condition_grade_repository.py  ConditionGradeRepository impl.
      workflow_state_mapper.py            WorkflowState <-> DynamoDB item
      dynamodb_workflow_state_repository.py   WorkflowStateRepository impl.
      disposition_mapper.py               DispositionDecision <-> DynamoDB item (Phase 4A)
      dynamodb_disposition_repository.py  DispositionRepository impl. (Phase 4A)
    storage/
      s3_image_storage.py                 ImageStoragePort impl.

  api/
    routers/
      health.py                           GET /health
      returns.py                          Phase 2 return intake endpoints
      grades.py                           Phase 3 grading + workflow endpoints
      dispositions.py                     Phase 4A disposition routing endpoints
    schemas/
      common.py                           BaseSchema, error/health schemas
      return_schemas.py                   Phase 2 request/response models
      grade_schemas.py                    Grading, workflow, review schemas
      disposition_schemas.py              Disposition request/response schemas (Phase 4A)
      health_card_schemas.py              Health Card schemas (future)
      prediction_schemas.py               PreventIQ schemas (future)

tests/
  conftest.py                             Shared fixtures
  factories/domain_factories.py           Entity builders for tests
  fakes/
    fake_return_repository.py             In-memory ReturnRepository
    fake_image_storage.py                 In-memory ImageStoragePort
    fake_grading_port.py                  In-memory GradingPort
    fake_description_generation_port.py   In-memory DescriptionGenerationPort
    fake_condition_grade_repository.py    In-memory ConditionGradeRepository
    fake_human_review_queue_port.py       In-memory HumanReviewQueuePort
    fake_workflow_state_repository.py     In-memory WorkflowStateRepository
  unit/
    domain/                               Entity/VO unit tests
    application/                          Use case + service unit tests
    infrastructure/                       Adapter + mapper unit tests
  integration/
    test_returns_api.py                   Phase 2 API integration tests
    test_grades_api.py                    Phase 3 grading API tests

docs/
  PROJECT_STATE.md                        Living status document
  PROJECT_RECOVERY_PROMPT.md              Prompt to resume in a new session
  REPOSITORY_MAP.md                       This file
  CHAT_MIGRATION.md                       Chat handoff log
  phases/
    phase-03a-condition-grading-core.md   Phase 3A documentation
    phase-03ba-bedrock-description.md     Phase 3Ba documentation
    phase-03bb-workflow-queue.md           Phase 3Bb documentation
```

## Single-Table DynamoDB Layout (`returniq-main`)

| Item | PK | SK | GSI1 (seller-index) | GSI2 (buyer-index) |
|---|---|---|---|---|
| Return Request | `RETURN#{id}` | `REQUEST` | `SELLER#{seller_id}` / `RETURN#{ts}#{id}` | `BUYER#{buyer_id}` / `RETURN#{ts}#{id}` |
| Condition Grade | `RETURN#{id}` | `CONDITION_GRADE` | — | — |
| Workflow State | `RETURN#{id}` | `WORKFLOW_STATE` | — | — |
| Disposition | `RETURN#{id}` | `DISPOSITION` | — | — |
| Health Card | `RETURN#{id}` | `HEALTH_CARD` | `SELLER#{seller_id}` / ... | `BUYER#{buyer_id}` / ... |
| QR Token | `QR#{token}` | `META` | — | — |
| Fraud Record | `FRAUD#{buyer_id}` | `SKU#{sku_id}` | — | — |
| Flywheel Outcome | `OUTCOME#{return_id}` | `RESULT` | — | — |
