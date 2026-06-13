# Project State

_Last updated: end of Phase 2 — Return Intake APIs._

## Summary

ReturnIQ backend is a Clean Architecture / DDD FastAPI service. Domain
layer (entities, value objects, exceptions) and Phase 2 application +
infrastructure layers for the **Return Intake** bounded context are
complete, tested, and passing `mypy --strict` and `ruff`.

## What Exists Today

### Domain (`app/domain`)
- Entities: `ReturnRequest` (lifecycle: `AWAITING_IMAGES -> IMAGES_RECEIVED
  -> GRADED -> ROUTED -> HEALTH_CARD_ISSUED -> ...`), `ConditionGrade`,
  `HealthCard`, `QRToken`.
- Value objects: `ReturnId` (ULID), `ImageKey`, `Grade`, `Route`,
  `ConfidenceScore`, `Money` - all immutable, self-validating.
- `app/domain/exceptions.py` - full exception taxonomy mapped to HTTP
  status codes in `app/main.py`.

### Application (`app/application`)
- Ports (interfaces): `ReturnRepository`, `HealthCardRepository`,
  `ImageStoragePort`, `GradingPort`, `NotificationPort`, `PredictionPort`,
  `FraudPort`.
- **Phase 2 use cases** (`app/application/use_cases`):
  `CreateReturnUseCase`, `GetReturnUseCase`, `GetReturnStatusUseCase`,
  `CompleteImageUploadUseCase`. DTOs in `dto.py`.

### Infrastructure (`app/infrastructure`)
- `aws/clients.py` - boto3 DynamoDB Table / S3 client factories.
- `persistence/dynamodb_return_repository.py` +
  `return_item_mapper.py` - single-table DynamoDB adapter for
  `ReturnRepository`.
- `storage/s3_image_storage.py` - `ImageStoragePort` via presigned URLs.
- `logging.py` - structlog configuration (auto-configures on first
  `get_logger` call).

### API (`app/api`)
- `routers/health.py` - `/health`.
- `routers/returns.py` - `/returns` CRUD + status + image completion
  (Phase 2, see `docs/phases/phase-02-return-intake.md`).
- `schemas/*` - Pydantic v2 request/response models for returns,
  health cards, predictions.

### Wiring
- `app/container.py` - `dependency-injector` `DeclarativeContainer`,
  wires `app.api.routers`.
- `app/main.py` - `create_app()`, exception handlers for every domain
  exception, lifespan wires the container.

### Tests
- `tests/unit/application/*` - use case tests against in-memory fakes
  (`tests/fakes`, `tests/factories`).
- `tests/integration/test_returns_api.py` - full API tests against
  `moto`-mocked AWS.
- **18/18 passing.** `mypy app` clean. `ruff check .` clean.

## What Is NOT Implemented Yet

- Step Functions trigger when a return reaches `IMAGES_RECEIVED`.
- Rekognition grading / Bedrock damage description adapters
  (`GradingPort` has no implementation).
- Router / fraud-check application services.
- `HealthCardRepository` DynamoDB implementation, QR generation/issuance,
  `/verify/{qr_token}`.
- `NotificationPort` (SNS/SES) and `PredictionPort` (SageMaker)
  implementations.
- Authentication on API Gateway (API key for hackathon, Cognito for prod).
- Seller/buyer return listing endpoints (repository methods
  `get_by_seller` / `get_by_buyer` exist and are tested at the
  repository layer but have no API endpoints yet).

## How To Run

```bash
make install
docker compose up -d         # dynamodb-local + admin UI on :8002
cp .env.example .env          # adjust DYNAMODB_ENDPOINT_URL etc.
make dev                      # uvicorn --reload on :8000
make check                     # ruff + mypy + pytest
```

## Next Phase (Phase 3 - Recommended)

Build the grading + routing pipeline:
1. `RekognitionGradingAdapter` + `BedrockDescriptionAdapter` implementing
   `GradingPort`.
2. `GradeReturnUseCase` orchestrating grading -> confidence check ->
   routing decision -> fraud check.
3. Workflow trigger port + Step Functions (or in-process orchestration
   for local dev) invoked once `IMAGES_RECEIVED`.
4. Extend `ReturnRequest` persistence to store `ConditionGrade` and
   routing outcome (new DynamoDB items or extended attributes).

See `docs/PROJECT_RECOVERY_PROMPT.md` to resume work in a new session.
