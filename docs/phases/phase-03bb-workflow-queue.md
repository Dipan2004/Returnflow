# Phase 3Bb — Human Review Queue + Grading Workflow Orchestration

## Objective
Complete the Condition Assessment pipeline by implementing the Human Review Queue (SQS), Grading Workflow Orchestration service with step tracking, and the remaining grading API endpoints (`/workflow`, `/review-status`).

## Scope
- `HumanReviewRequest` entity — domain object representing a review escalation with priority classification
- `WorkflowState` entity — tracks step-by-step execution of the grading pipeline
- `HumanReviewQueuePort` — application port for queue publishing
- `WorkflowStateRepository` — application port for workflow persistence
- `SQSHumanReviewAdapter` — SQS infrastructure adapter with retry + DLQ support
- `GradingWorkflowService` — orchestration service coordinating: Rekognition → Confidence Gate → Bedrock/SQS → Persist
- `DynamoDBWorkflowStateRepository` — DynamoDB persistence for workflow state
- API: `POST /grades/process`, `GET /grades/{return_id}/workflow`, `GET /grades/{return_id}/review-status`
- Full test suite: domain, use case, adapter, mapper, integration

## Files Added
```
app/domain/entities/human_review_request.py
app/domain/entities/workflow_state.py
app/application/ports/human_review_queue_port.py
app/application/ports/workflow_state_repository.py
app/application/services/__init__.py
app/application/services/grading_workflow_service.py
app/application/use_cases/get_workflow_state_use_case.py
app/application/use_cases/get_review_status_use_case.py
app/infrastructure/adapters/sqs/__init__.py
app/infrastructure/adapters/sqs/sqs_human_review_adapter.py
app/infrastructure/persistence/workflow_state_mapper.py
app/infrastructure/persistence/dynamodb_workflow_state_repository.py
tests/fakes/fake_human_review_queue_port.py
tests/fakes/fake_workflow_state_repository.py
tests/unit/domain/test_human_review_request.py
tests/unit/domain/test_workflow_state.py
tests/unit/application/test_grading_workflow_service.py
tests/unit/application/test_get_workflow_state_use_case.py
tests/unit/application/test_get_review_status_use_case.py
tests/unit/infrastructure/test_sqs_human_review_adapter.py
tests/unit/infrastructure/test_workflow_state_mapper.py
tests/integration/test_grades_api.py
docs/phases/phase-03bb-workflow-queue.md
```

## Files Modified
```
app/config.py                               — added sqs_endpoint_url field
app/container.py                            — registered sqs_client, human_review_queue, workflow_state_repository, grading_workflow_service, new use cases
app/infrastructure/aws/clients.py           — added build_sqs_client
app/application/use_cases/dto.py            — added StepRecordDTO, WorkflowStateResult, ReviewStatusResult
app/api/schemas/grade_schemas.py            — added WorkflowStateResponse, ReviewStatusResponse, StepRecordResponse
app/api/routers/grades.py                   — added POST /grades/process, GET .../workflow, GET .../review-status
pyproject.toml                              — added boto3-stubs[sqs], moto[sqs]
```

## Architecture Decisions

### Workflow Orchestration as Application Service (not Step Functions client)
The `GradingWorkflowService` orchestrates the grading pipeline in-process rather than calling AWS Step Functions directly. This enables:
- Local development without AWS
- Full unit testability with fakes
- Step Functions Express Workflow is the production deployment target, but the orchestration logic stays decoupled

### WorkflowState as Domain Entity
Step execution tracking is modeled as a domain entity (`WorkflowState`) persisted to DynamoDB. This gives:
- Visibility into pipeline progress via `GET /grades/{id}/workflow`
- Failure forensics with per-step timing and error messages
- Foundation for future Step Functions status synchronization

### SQS Adapter with Retry
The SQS adapter retries up to `max_retries` times with linear backoff. If all retries fail, `InfrastructureError` propagates to the workflow service which records the failure in the workflow state before re-raising.

### Human Review Priority Classification
Priority is determined by confidence distance from threshold:
- CRITICAL: confidence < 40%
- HIGH: confidence < 60%
- MEDIUM: confidence < 75%
- LOW: confidence >= 75% but < threshold (87%)

This enables downstream queue consumers to process critical items first.

### Dual Grading Endpoints
- `POST /grades` — original simple grading (no workflow tracking, backward compatible)
- `POST /grades/process` — full workflow with step tracking, SQS dispatch, and persistence

## Infrastructure Decisions
- DynamoDB item: `PK=RETURN#{id}`, `SK=WORKFLOW_STATE` — follows existing single-table pattern
- SQS message attributes include ReturnId, Priority, and Confidence for message filtering
- SQS DLQ handling: adapter raises `InfrastructureError` after retry exhaustion; caller decides recovery

## Test Coverage
- `test_human_review_request.py` — 8 cases: creation, validation, priority thresholds, payload
- `test_workflow_state.py` — 9 cases: lifecycle, step recording, failure, timing
- `test_grading_workflow_service.py` — 7 cases: happy path, human review, not found, persistence, metadata, grading failure, SQS failure
- `test_get_workflow_state_use_case.py` — 3 cases: found, not found, timing
- `test_get_review_status_use_case.py` — 4 cases: not routed, routed, not found, no workflow
- `test_sqs_human_review_adapter.py` — 5 cases: success, attributes, retry, exhaustion, no retry
- `test_workflow_state_mapper.py` — 5 cases: keys, steps, roundtrip, failed, null step
- `test_grades_api.py` — 3 integration cases: 404 responses for all new endpoints
- **Total: 44 new tests, 95 total suite passing**

## Open Issues
- Step Functions ASL (Amazon States Language) definition not included — infrastructure concern, deployed separately via SAM template
- SQS DLQ configuration (redrive policy) is infrastructure-level, not in application code
- No consumer-side implementation for the human review queue (future phase)

## Remaining Work — Phase 4
- Disposition Router (Lambda decision engine)
- Fraud Detection Layer
- Health Card Generation + QR
- SNS Buyer Notifications
- PreventIQ (SageMaker integration)
- Flywheel Dashboard APIs

## Handoff Instructions
1. Load `docs/PROJECT_STATE.md`, `docs/REPOSITORY_MAP.md`, this file.
2. Run `pytest tests/` — all 95 tests should pass.
3. Phase 4 entry point: implement `DispositionRouter` as a domain service, then `FraudPort` adapter.
4. The `GradingWorkflowService` is the pattern to follow for the disposition orchestration service.
5. `POST /grades/process` is the production endpoint — triggers full grading + workflow + queue dispatch.
