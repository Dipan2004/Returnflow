# Project Recovery Prompt

Use this to resume ReturnIQ development in a new session.

## Context

ReturnIQ is an intelligent returns disposition engine for Amazon HackOn Season 6.
Serverless FastAPI backend using Clean Architecture / DDD with dependency injection,
Pydantic v2, and AWS services (Rekognition, Bedrock, DynamoDB, SQS, S3).

## Current State: Phase 5B Complete

All phases through 5B implemented:
- Phase 1-2: Domain foundation + Return intake APIs
- Phase 3A/3Ba/3Bb: CV grading + Bedrock descriptions + Workflow + SQS
- Phase 4A-D: Disposition + Fraud + Buyer Match + Orchestration
- Phase 5A: Health Card + QR token generation
- Phase 5B: QR Verification + Tamper Detection

**352 tests passing.** `ruff check .` clean. `mypy app` clean.

## Key Patterns

1. Ports & Adapters: abstract ports in `app/application/ports/`, implementations in `app/infrastructure/`
2. Fakes for testing: every port has an in-memory fake in `tests/fakes/`
3. DI Container: `dependency-injector` in `app/container.py`
4. Single-table DynamoDB: PK/SK pattern with GSIs
5. Async I/O: all boto3 wrapped in `asyncio.to_thread()`
6. Domain services: business rules in `app/domain/services/`

## Read These Files First

1. `docs/PROJECT_STATE.md`
2. `docs/phases/phase-05b-qr-verification.md`
3. `app/container.py`
4. `app/main.py`

## Next Phase: 6 — Notifications + PreventIQ

1. SNS buyer notification on P2P match
2. SageMaker PreventIQ return prediction widget
3. Flywheel dashboard aggregation APIs
