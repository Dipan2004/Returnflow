# Phase 5A — Health Card Domain + QR Generation

## Objective
Create the Product Health Card domain — the permanent provenance record for every returned item — with QR code generation, tamper-evident token issuance, and full persistence.

## What Was Built
- HealthCard aggregate (existing Phase 1 entity, now fully wired)
- QRToken aggregate (existing Phase 1 entity, now fully wired)
- QRCodeGenerationService domain service (token creation, URL building, PNG generation)
- QRCodeStoragePort abstraction with LocalQRCodeStorage adapter
- DynamoDB persistence for HealthCard and QRToken (single-table design)
- GenerateHealthCardUseCase, GetHealthCardUseCase, GetHealthCardByQRUseCase
- API endpoints: POST /health-cards/generate/{return_id}, GET /health-cards/{return_id}, GET /health-cards/by-qr/{qr_token}

## Files Added
```
app/application/ports/qr_storage_port.py
app/application/use_cases/health_card_dto.py
app/application/use_cases/generate_health_card_use_case.py
app/application/use_cases/get_health_card_use_case.py
app/application/use_cases/get_health_card_by_qr_use_case.py
app/domain/services/qr_generation_service.py
app/infrastructure/persistence/health_card_mapper.py
app/infrastructure/persistence/qr_token_mapper.py
app/infrastructure/persistence/dynamodb_health_card_repository.py
app/infrastructure/adapters/qr_storage/__init__.py
app/infrastructure/adapters/qr_storage/local_qr_storage.py
app/api/routers/health_cards.py
tests/fakes/fake_health_card_repository.py
tests/fakes/fake_qr_storage_port.py
tests/unit/domain/test_health_card_qr.py
tests/unit/application/test_health_card_use_cases.py
tests/unit/infrastructure/test_health_card_mapper.py
tests/integration/test_health_cards_api.py
```

## Files Modified
```
app/api/schemas/health_card_schemas.py   — replaced stub with full schemas
app/container.py                         — added health_card_repository, qr_storage_port, qr_generation_service, 3 use cases
app/main.py                              — registered health_cards router
```

## Architecture Decisions
- HealthCard uses return_id as identity (one card per return)
- QRToken stored separately (PK=QR#{token}, SK=META) for O(1) lookup by token
- QRCodeStoragePort abstracts image storage (local now, S3 later)
- QRCodeGenerationService is a domain service (no I/O except image bytes generation)
- Health card generation requires both ConditionGrade and DispositionDecision to exist first

## DynamoDB Items
| Entity | PK | SK |
|--------|----|----|
| HealthCard | RETURN#{id} | HEALTH_CARD |
| QRToken | QR#{token} | META |

## Test Coverage
- Domain: 12 tests (HealthCard state transitions, validation, QRToken lifecycle)
- Use cases: 6 tests (generate, get, get-by-qr, error paths)
- Infrastructure: 5 mapper roundtrip tests
- Integration: 3 API endpoint tests
- Total: 26 new tests

## Handoff
- Health Card generation is downstream of disposition — call POST /health-cards/generate/{return_id} after disposition is calculated
- QR token is consumed by the verification flow (Phase 5B)
- Next: Phase 5B implements tamper-evident QR verification
