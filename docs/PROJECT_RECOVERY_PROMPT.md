# Project Recovery Prompt

Use this to resume ReturnIQ development in a new Claude session.

## Context

ReturnIQ is an intelligent returns disposition engine for Amazon HackOn Season 6.
It's a serverless FastAPI backend using Clean Architecture / DDD patterns with
dependency injection, Pydantic v2, and AWS services (Rekognition, Bedrock, DynamoDB, SQS, S3).

## Current State: Phase 3Bb Complete

The Condition Assessment pipeline is fully implemented:
- Phase 1: Domain foundation (entities, VOs, exceptions)
- Phase 2: Return intake APIs (create, status, image upload)
- Phase 3A: Rekognition grading adapter + grade mapper + confidence gate
- Phase 3Ba: Bedrock Claude Haiku damage description adapter
- Phase 3Bb: SQS human review queue + GradingWorkflowService + workflow tracking APIs

**95 tests passing.** All green.

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
3. `docs/phases/phase-03bb-workflow-queue.md` — latest phase details
4. `app/container.py` — all wiring in one place
5. `app/application/services/grading_workflow_service.py` — orchestration pattern

## Next Phase: 4 — Disposition Routing

Implement the routing decision engine:
1. `DispositionRouter` domain service: Grade A → P2P/Resell, Grade B → Refurbish, Grade C → Donate
2. `FraudCheckService`: bulk-buy detection (10+ units in 72h blocks P2P)
3. `HealthCardGenerator`: DynamoDB write + QR code → S3
4. `SNSNotificationAdapter`: buyer SMS/email
5. APIs: `POST /disposition/route`, `GET /health-cards/{id}`, `GET /verify/{qr_token}`

Follow the same pattern: port → adapter → service → use case → router → test.
