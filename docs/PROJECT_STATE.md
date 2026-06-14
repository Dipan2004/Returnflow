# Project State

_Last updated: end of Phase 3Bb — Human Review Queue + Grading Workflow._

## Summary

ReturnIQ backend is a Clean Architecture / DDD FastAPI service. The full
Condition Assessment pipeline is now complete: Rekognition CV grading,
Bedrock damage description, confidence gate, SQS human review queue,
and workflow orchestration — all tested and passing.

## What Exists Today

### Domain (`app/domain`)
- Entities: `ReturnRequest`, `ConditionGrade`, `HumanReviewRequest`,
  `WorkflowState`, `HealthCard`, `QRToken`, `BuyerMatch`,
  `DispositionDecision`, `FraudAssessment`.
- Value objects: `ReturnId` (ULID), `ImageKey`, `Grade`, `Route`,
  `ConfidenceScore`, `Money`.
- Domain services: `ConfidenceGate` (human review decision).
- `app/domain/exceptions.py` — full exception taxonomy.

### Application (`app/application`)
- Ports: `ReturnRepository`, `ImageStoragePort`, `GradingPort`,
  `DescriptionGenerationPort`, `ConditionGradeRepository`,
  `HumanReviewQueuePort`, `WorkflowStateRepository`,
  `HealthCardRepository`, `NotificationPort`, `PredictionPort`, `FraudPort`.
- Services: `GradingWorkflowService` (orchestrates full grading pipeline).
- Use cases: `CreateReturnUseCase`, `GetReturnUseCase`,
  `GetReturnStatusUseCase`, `CompleteImageUploadUseCase`,
  `ProcessGradingUseCase`, `GetConditionGradeUseCase`,
  `GetWorkflowStateUseCase`, `GetReviewStatusUseCase`.

### Infrastructure (`app/infrastructure`)
- `aws/clients.py` — boto3 factories for DynamoDB, S3, Rekognition,
  Bedrock, SQS.
- `adapters/grading/` — `RekognitionGradingAdapter`, `grade_mapper`,
  `models`.
- `adapters/bedrock/` — `BedrockDescriptionAdapter`, `prompt_templates`,
  `response_parser`.
- `adapters/sqs/` — `SQSHumanReviewAdapter` with retry logic.
- `persistence/` — DynamoDB repositories for ReturnRequest,
  ConditionGrade, WorkflowState.
- `storage/` — S3 image storage with presigned URLs.

### API (`app/api`)
- `GET /health`
- `POST /returns`, `GET /returns/{id}`, `GET /returns/{id}/status`,
  `POST /returns/{id}/images/complete`
- `POST /grades` (simple grading, backward compatible)
- `POST /grades/process` (full workflow with SQS + tracking)
- `GET /grades/{id}` (condition grade)
- `GET /grades/{id}/workflow` (step-by-step execution state)
- `GET /grades/{id}/review-status` (human review status)

### Tests
- **95 tests passing.** Unit (domain, application, infrastructure) +
  integration (API with moto-mocked AWS).
- Coverage: new Phase 3B code at 90%+.

## What Is NOT Implemented Yet

- Disposition Router (Grade → Route decision engine).
- Fraud Detection Layer.
- Health Card Generation + QR code + tamper verification.
- SNS/SES Buyer Notifications.
- SageMaker PreventIQ (return prediction).
- Flywheel Dashboard APIs.
- Step Functions ASL template (deployed via SAM, not in app code).
- Authentication (API key / Cognito).

## How To Run

```bash
make install
docker compose up -d          # dynamodb-local + admin UI on :8002
cp .env.example .env          # adjust endpoints
make dev                      # uvicorn --reload on :8000
make check                    # ruff + mypy + pytest
```

## Phase History

| Phase | Description | Status |
|---|---|---|
| 1 | Domain Foundation | ✅ Complete |
| 2 | Return Intake APIs | ✅ Complete |
| 3A | Condition Grading Core (Rekognition) | ✅ Complete |
| 3Ba | Bedrock Damage Description | ✅ Complete |
| 3Bb | Human Review Queue + Workflow | ✅ Complete |
| 4 | Disposition Router + Fraud | 🔜 Next |

## Next Phase (Phase 4 - Recommended)

Build the disposition routing pipeline:
1. `DispositionRouter` domain service with Grade→Route decision tree.
2. `FraudCheckService` with bulk-buy detection.
3. `HealthCardGenerator` + QR code generation.
4. SNS buyer notification adapter.
5. API endpoints for health cards and disposition.
