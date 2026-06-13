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
      return_request.py                   ReturnRequest aggregate (Phase 2 core)
      condition_grade.py                  Grading result entity
      health_card.py                      Health Card aggregate
      qr_token.py                         Tamper-evident QR token entity
      buyer_match.py                      P2P buyer match entity
      disposition_decision.py             Routing decision entity
      fraud_assessment.py                 Fraud check result entity
    events/                               Domain events (return_submitted,
                                           grading_completed, disposition_routed)

  application/
    ports/
      return_repository.py                ReturnRepository (Phase 2 - implemented)
      image_storage_port.py               ImageStoragePort (Phase 2 - implemented)
      health_card_repository.py           HealthCardRepository (not yet impl.)
      grading_port.py                     GradingPort (not yet impl.)
      notification_port.py                NotificationPort (not yet impl.)
      prediction_port.py                  PredictionPort (not yet impl.)
      fraud_port.py                       FraudPort (not yet impl.)
    use_cases/
      dto.py                               Shared result DTOs for Phase 2
      create_return_use_case.py            POST /returns
      get_return_use_case.py               GET /returns/{id}
      get_return_status_use_case.py        GET /returns/{id}/status
      complete_image_upload_use_case.py    POST /returns/{id}/images/complete

  infrastructure/
    logging.py                             structlog configuration
    aws/clients.py                         boto3 Table/S3 client factories
    persistence/
      return_item_mapper.py                ReturnRequest <-> DynamoDB item
      dynamodb_return_repository.py        ReturnRepository impl.
    storage/
      s3_image_storage.py                  ImageStoragePort impl.

  api/
    routers/
      health.py                            GET /health
      returns.py                           Phase 2 return intake endpoints
    schemas/
      common.py                            BaseSchema, error/health schemas
      return_schemas.py                    Phase 2 request/response models
      health_card_schemas.py               Health Card / flywheel schemas
                                            (used by future phases)
      prediction_schemas.py                PreventIQ schemas (future)

tests/
  conftest.py                              Shared fixtures (fake repo/storage)
  factories/domain_factories.py            Entity builders for tests
  fakes/
    fake_return_repository.py              In-memory ReturnRepository
    fake_image_storage.py                  In-memory ImageStoragePort
  unit/
    domain/                                 Entity/value-object unit tests
    application/                            Phase 2 use case unit tests
  integration/
    conftest.py                             moto-backed DynamoDB + S3 + TestClient
    test_returns_api.py                     Full Phase 2 API test suite

docs/
  PROJECT_STATE.md                          Living status document
  PROJECT_RECOVERY_PROMPT.md                Prompt to resume in a new session
  REPOSITORY_MAP.md                         This file
  CHAT_MIGRATION.md                         Chat handoff log
  phases/
    phase-01-foundation.md                  Domain layer foundation
    phase-02-return-intake.md               Return Intake APIs (current)
```

## Single-Table DynamoDB Layout (`returniq-main`)

| Item | PK | SK | GSI1 (seller-index) | GSI2 (buyer-index) |
|---|---|---|---|---|
| Return Request | `RETURN#{id}` | `REQUEST` | `SELLER#{seller_id}` / `RETURN#{ts}#{id}` | `BUYER#{buyer_id}` / `RETURN#{ts}#{id}` |

Future items (Health Card, QR Token, Fraud Record, Flywheel Outcome) will
follow the key conventions documented in the architecture spec and be
added to this table once their phases land.
