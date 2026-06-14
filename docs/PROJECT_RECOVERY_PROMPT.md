# Project Recovery Prompt

Use this to resume ReturnIQ development in a new Claude session.

## Context

ReturnIQ is an intelligent returns disposition engine for Amazon HackOn Season 6.
It's a serverless FastAPI backend using Clean Architecture / DDD patterns with
dependency injection, Pydantic v2, and AWS services (Rekognition, Bedrock, DynamoDB, SQS, S3).

## Current State: Phase 4A Complete

The Condition Assessment pipeline and Disposition Engine are fully implemented:
- Phase 1: Domain foundation (entities, VOs, exceptions)
- Phase 2: Return intake APIs (create, status, image upload)
- Phase 3A: Rekognition grading adapter + grade mapper + confidence gate
- Phase 3Ba: Bedrock Claude Haiku damage description adapter
- Phase 3Bb: SQS human review queue + GradingWorkflowService + workflow tracking APIs
- Phase 4A: Disposition Engine (Grade→Route decision tree, recovery values, persistence, APIs)

**162 tests passing.** `ruff check .` clean. `mypy app` clean.

## Key Architecture Patterns

1. **Ports & Adapters**: All external services behind abstract ports in `app/application/ports/`
2. **Fakes for testing**: Every port has an in-memory fake in `tests/fakes/`
3. **DI Container**: `dependency-injector` DeclarativeContainer in `app/container.py`
4. **Single-table DynamoDB**: PK/SK pattern with GSIs for seller/buyer queries
5. **Async throughout**: All I/O wrapped in `asyncio.to_thread()` for boto3 calls
6. **Domain services**: Business rules in `app/domain/services/`, orchestration in `app/application/services/`

## How to Resume

```bash
cd Returnflow-main
.venv\Scripts\activate   # or source .venv/bin/activate
pytest tests/            # verify 95 tests pass
```

## Read These Files First

1. `docs/PROJECT_STATE.md` — what exists, what doesn't
2. `docs/REPOSITORY_MAP.md` — file layout with descriptions
3. `docs/phases/phase-04a-disposition-engine.md` — latest phase details
4. `app/container.py` — all wiring in one place
5. `app/domain/services/disposition_engine.py` — routing business rules
6. `app/application/services/grading_workflow_service.py` — orchestration pattern

## Next Phase: 4B — Fraud Detection + Health Cards

Implement:
1. `FraudCheckService`: bulk-buy detection (10+ units in 72h blocks P2P)
2. `HealthCardGenerator`: DynamoDB write + QR code → S3
3. `SNSNotificationAdapter`: buyer SMS/email
4. Real `DemandSignalPort` adapter (DynamoDB demand index)
5. Real `ProductCatalogPort` adapter (DynamoDB catalog or hardcoded demo data)
6. APIs: `GET /health-cards/{id}`, `GET /verify/{qr_token}`

Follow the same pattern: port → adapter → service → use case → router → test.
