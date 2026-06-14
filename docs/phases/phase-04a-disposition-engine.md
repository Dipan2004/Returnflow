# Phase 4A — Disposition Engine

## Objective
Implement the smart disposition routing engine that maps condition grades to optimal routes (P2P/Resell/Refurbish/Donate/Scrap) with recovery value calculations.

## Scope
- `DispositionDecision` domain entity with routing logic and validation
- `DispositionEngine` domain service with PRD-compliant business rules
- `DemandSignalPort` + `ProductCatalogPort` application ports
- `DispositionRepository` application port + DynamoDB adapter
- `CalculateDispositionUseCase` + `GetDispositionUseCase`
- API: `POST /dispositions/calculate`, `GET /dispositions/{return_id}`
- Full test suite: domain, use case, mapper, fakes, integration

## Business Rules (PRD)
| Grade | Route | Recovery % |
|-------|-------|-----------|
| A (demand exists within 5km) | P2P | 65% |
| A (no demand) | RESELL | 75% |
| B | REFURBISH | 55% |
| C | DONATE | 0% |
| DONATE | DONATE | 0% |
| SCRAP | SCRAP | 0% |

- Liquidation baseline = 5% MRP
- Value delta = recovery_value - liquidation_baseline
- Fraud-flagged accounts are forced to RESELL (no P2P)

## Files Added
```
app/domain/services/disposition_engine.py
app/application/ports/demand_signal_port.py
app/application/ports/product_catalog_port.py
app/application/ports/disposition_repository.py
app/application/use_cases/disposition_dto.py
app/application/use_cases/calculate_disposition_use_case.py
app/application/use_cases/get_disposition_use_case.py
app/infrastructure/persistence/disposition_mapper.py
app/infrastructure/persistence/dynamodb_disposition_repository.py
app/api/schemas/disposition_schemas.py
app/api/routers/dispositions.py
tests/fakes/fake_demand_signal_port.py
tests/fakes/fake_product_catalog_port.py
tests/fakes/fake_disposition_repository.py
tests/unit/domain/test_disposition_decision.py
tests/unit/application/test_calculate_disposition_use_case.py
tests/unit/application/test_get_disposition_use_case.py
tests/unit/application/test_fake_ports.py
tests/unit/infrastructure/test_disposition_mapper.py
tests/integration/test_dispositions_api.py
docs/phases/phase-04a-disposition-engine.md
```

## Files Modified
```
app/container.py    — added disposition_repository, disposition_engine,
                      calculate_disposition_use_case, get_disposition_use_case
app/main.py         — include dispositions router
```

## Architecture Decisions
- `DispositionEngine` is a pure domain service (no I/O) — all routing rules live here.
- `DispositionDecision.decide()` is the factory method that encapsulates the routing decision tree.
- Container uses `providers.Object(None)` for DemandSignalPort and ProductCatalogPort since
  real adapters (e.g. DynamoDB demand index, product catalog API) belong to future phases.
  Tests use proper fakes.
- Recovery percentages are constants in the engine, matching PRD exactly.

## Test Coverage
- Domain: 28 tests (routing, recovery values, validation, engine)
- Use cases: 12 + 3 + 12 = 27 tests (calculate, get, fake port contracts)
- Infrastructure: 6 mapper roundtrip tests
- Integration: 6 API endpoint tests
- **Total: 67 Phase 4A tests**

## Handoff Instructions
1. All 162 tests pass. `ruff check .` clean. `mypy app` clean.
2. DemandSignalPort/ProductCatalogPort wired as `Object(None)` in container. 
   Future phases implement real adapters (DynamoDB demand table, product catalog API).
3. Next: Phase 4B — Fraud Detection, Health Card Generation, SNS notifications.
