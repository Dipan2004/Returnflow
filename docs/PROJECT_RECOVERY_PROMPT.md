# Project Recovery Prompt

Use this to resume ReturnIQ development in a new Claude session.

## Context

ReturnIQ is an intelligent returns disposition engine for Amazon HackOn Season 6.
It's a serverless FastAPI backend using Clean Architecture / DDD patterns with
dependency injection, Pydantic v2, and AWS services (Rekognition, Bedrock, DynamoDB, SQS, S3).

## Current State: Phase 4B Complete

All phases through 4B implemented:
- Phase 1: Domain foundation
- Phase 2: Return intake APIs
- Phase 3A/3Ba/3Bb: Condition grading + Bedrock + Workflow + SQS
- Phase 4A: Disposition Engine
- Phase 4B: Fraud Detection Engine (multi-signal, route override)

**209 tests passing.** `ruff check .` clean. `mypy app` clean.

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
3. `docs/phases/phase-04b-fraud-engine.md` — latest phase details
4. `app/container.py` — all wiring in one place
5. `app/domain/services/fraud_engine.py` — fraud signal evaluation
6. `app/domain/services/disposition_engine.py` — routing business rules

## Next Phase: 4C — Health Cards + QR + Notifications

Implement:
1. `HealthCardGenerator`: DynamoDB write + QR code → S3
2. `QRVerificationService`: tamper-evident scan tracking
3. `SNSNotificationAdapter`: buyer SMS/email on P2P match
4. Real `FraudHistoryPort` adapter (DynamoDB buyer history)
5. Real `DemandSignalPort` adapter (DynamoDB demand index)
6. APIs: `GET /health-cards/{id}`, `GET /verify/{qr_token}`

Follow the same pattern: port → adapter → service → use case → router → test.
