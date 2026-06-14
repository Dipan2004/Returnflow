# Phase 4B — Fraud Detection Engine

## Objective
Implement FraudIQ — a multi-signal fraud assessment engine that calculates risk scores,
classifies risk levels (LOW/MEDIUM/HIGH), and overrides disposition routing for HIGH-risk accounts.

## Business Rules
- Risk levels: LOW (0-39), MEDIUM (40-69), HIGH (70-100)
- 4 fraud signals with individual weights:
  - Excessive return frequency: weight 30, threshold 5 returns in window
  - High-value return frequency: weight 25, threshold 3 in window
  - Repeat SKU returns: weight 25, threshold 2 in window
  - Suspicious return velocity: weight 20, threshold 3 in 24h
- Score = sum of triggered signal weights, capped at 100
- HIGH risk MUST override route to RESELL (e.g., P2P → RESELL)
- Override reason stored with original route, overridden route, risk details

## Files Added
```
app/domain/services/fraud_engine.py
app/application/ports/fraud_history_port.py
app/application/ports/fraud_repository.py
app/application/use_cases/fraud_dto.py
app/application/use_cases/assess_fraud_use_case.py
app/application/use_cases/get_fraud_assessment_use_case.py
app/infrastructure/persistence/fraud_mapper.py
app/infrastructure/persistence/dynamodb_fraud_repository.py
app/api/schemas/fraud_schemas.py
app/api/routers/fraud.py
tests/fakes/fake_fraud_history_port.py
tests/fakes/fake_fraud_repository.py
tests/unit/domain/test_fraud_assessment.py
tests/unit/domain/test_fraud_engine.py
tests/unit/application/test_assess_fraud_use_case.py
tests/unit/application/test_get_fraud_assessment_use_case.py
tests/unit/infrastructure/test_fraud_mapper.py
tests/integration/test_fraud_api.py
docs/phases/phase-04b-fraud-engine.md
```

## Files Modified
```
app/domain/entities/fraud_assessment.py   — replaced old bulk-buy scaffold with multi-signal system
app/container.py                          — added fraud_repository, fraud_engine, use case providers
app/main.py                               — added fraud router
```

## Architecture Decisions
- FraudEngine is a domain service with zero I/O — all signal evaluation is pure logic
- FraudHistoryPort abstracts buyer history retrieval (future: DynamoDB adapter)
- FraudRepository persists assessments to DynamoDB single-table (PK=RETURN#, SK=FRAUD_ASSESSMENT)
- Override is modeled as a value object (FraudOverrideReason) stored within the assessment
- Container wires FraudHistoryPort as Object(None) — real adapter deferred to infrastructure phase

## Test Coverage
- Domain entity: 20 tests (risk levels, signals, validation, override, score capping)
- Domain service (FraudEngine): 10 tests (all signal combos, override logic, no-override cases)
- Use cases: 7 + 3 = 10 tests (assess + get, persistence verification)
- Infrastructure mapper: 5 roundtrip tests
- Integration API: 2 tests (404, validation)
- **Total: 47 new tests, 209 total suite passing**

## Handoff Instructions
1. All 209 tests pass. `ruff check .` clean. `mypy app` clean.
2. FraudHistoryPort wired as Object(None) in container — implement real adapter in future.
3. Integration: call `POST /fraud/assess` with `original_route` from disposition result to check for override.
4. Next: Phase 4C — Health Card generation + QR tamper verification.
