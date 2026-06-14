# Repository Map

## DynamoDB Single-Table Layout (`returniq-main`)

| Item | PK | SK |
|------|----|----|
| Return Request | RETURN#{id} | REQUEST |
| Condition Grade | RETURN#{id} | CONDITION_GRADE |
| Workflow State | RETURN#{id} | WORKFLOW_STATE |
| Disposition | RETURN#{id} | DISPOSITION |
| Fraud Assessment | RETURN#{id} | FRAUD_ASSESSMENT |
| Buyer Match | RETURN#{id} | BUYER_MATCH |
| Health Card | RETURN#{id} | HEALTH_CARD |
| QR Token | QR#{token} | META |
| Verification Audit | QR#{token} | AUDIT#{timestamp} |
| Fraud History | FRAUD#{buyer_id} | SKU#{sku_id} |

## Directory Structure

```
app/
  main.py                         FastAPI app + exception handlers
  config.py                       AppConfig (pydantic-settings)
  container.py                    dependency-injector wiring

  domain/
    exceptions.py
    value_objects/
      return_id.py, image_key.py, grade.py, route.py,
      confidence_score.py, money.py, demand_level.py,
      demand_score.py, match_confidence.py, buyer_eligibility.py
    entities/
      return_request.py, condition_grade.py, disposition_decision.py,
      fraud_assessment.py, buyer_match_result.py, health_card.py,
      qr_token.py, human_review_request.py, workflow_state.py,
      verification_result.py, verification_audit.py
    services/
      human_review_decision.py, disposition_engine.py,
      disposition_orchestrator.py, fraud_engine.py,
      buyer_matching_engine.py, qr_generation_service.py
    events/

  application/
    ports/
      return_repository.py, image_storage_port.py, grading_port.py,
      description_generation_port.py, condition_grade_repository.py,
      human_review_queue_port.py, workflow_state_repository.py,
      disposition_repository.py, demand_signal_port.py,
      product_catalog_port.py, fraud_history_port.py,
      fraud_repository.py, demand_index_port.py,
      buyer_matching_port.py, buyer_match_repository.py,
      health_card_repository.py, qr_storage_port.py,
      verification_audit_repository.py
    services/
      grading_workflow_service.py
    use_cases/
      dto.py, disposition_dto.py, fraud_dto.py, buyer_match_dto.py,
      health_card_dto.py, orchestration_dto.py, verification_dto.py,
      create_return_use_case.py, get_return_use_case.py,
      get_return_status_use_case.py, complete_image_upload_use_case.py,
      process_grading_use_case.py, get_condition_grade_use_case.py,
      get_workflow_state_use_case.py, get_review_status_use_case.py,
      calculate_disposition_use_case.py, get_disposition_use_case.py,
      orchestrate_disposition_use_case.py,
      assess_fraud_use_case.py, get_fraud_assessment_use_case.py,
      match_buyer_use_case.py, get_buyer_match_use_case.py,
      generate_health_card_use_case.py, get_health_card_use_case.py,
      get_health_card_by_qr_use_case.py,
      verify_qr_token_use_case.py, get_verification_history_use_case.py

  infrastructure/
    logging.py
    aws/clients.py
    adapters/
      grading/ (rekognition_adapter, grade_mapper, models)
      bedrock/ (bedrock_description_adapter, prompt_templates, response_parser)
      sqs/ (sqs_human_review_adapter)
      catalog/ (in_memory_product_catalog)
      demand/ (in_memory_demand_signal)
      fraud/ (dynamodb_fraud_history_adapter)
      buyer_match/ (in_memory_demand_index, in_memory_buyer_matching_adapter)
      qr_storage/ (local_qr_storage)
    persistence/
      dynamodb_return_repository, return_item_mapper,
      dynamodb_condition_grade_repository, condition_grade_mapper,
      dynamodb_workflow_state_repository, workflow_state_mapper,
      dynamodb_disposition_repository, disposition_mapper,
      dynamodb_fraud_repository, fraud_mapper,
      dynamodb_buyer_match_repository, buyer_match_mapper,
      dynamodb_health_card_repository, health_card_mapper, qr_token_mapper,
      dynamodb_verification_audit_repository, verification_audit_mapper
    storage/
      s3_image_storage.py

  api/
    routers/
      health.py, returns.py, grades.py, dispositions.py,
      fraud.py, buyer_match.py, health_cards.py, verify.py
    schemas/
      common.py, return_schemas.py, grade_schemas.py,
      disposition_schemas.py, fraud_schemas.py, buyer_match_schemas.py,
      health_card_schemas.py, orchestration_schemas.py,
      verification_schemas.py

tests/
  conftest.py
  factories/domain_factories.py
  fakes/ (all in-memory port implementations)
  unit/domain/, unit/application/, unit/infrastructure/
  integration/ (moto-backed API tests)

docs/
  PROJECT_STATE.md, PROJECT_RECOVERY_PROMPT.md,
  REPOSITORY_MAP.md, CHAT_MIGRATION.md
  phases/ (phase-03a through phase-05b)
```
