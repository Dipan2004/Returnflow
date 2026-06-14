# Phase 5B — QR Verification + Tamper Detection

## Objective
Implement the tamper-evident verification workflow that delivery agents use to confirm package integrity at handoff. First scan succeeds; second scan triggers a POSSIBLE_TAMPERING alert.

## Verification Rules
| Scenario | Status | Alert |
|----------|--------|-------|
| First scan of valid token | VALID | NONE |
| Second+ scan (already consumed) | ALREADY_SCANNED | POSSIBLE_TAMPERING |
| Expired token | EXPIRED | NONE |
| Unknown token | NOT_FOUND | NONE |

## What Was Built
- VerificationResult value object (VALID / ALREADY_SCANNED / EXPIRED / NOT_FOUND)
- VerificationStatus and TamperAlert enums
- VerificationAuditEntry — immutable audit trail record
- VerifyQrTokenUseCase — core verification logic with tamper detection
- GetVerificationHistoryUseCase — retrieve full scan history
- VerificationAuditRepository port + DynamoDB implementation
- API: GET /verify/{qr_token}?agent_id=..., GET /verify/{qr_token}/history

## Race Condition Protection
- QRToken.consume() raises QRTokenAlreadyScannedError if already scanned
- DynamoDB conditional write in consume_qr_token ensures atomicity
- If concurrent scans race, only one gets VALID; others get POSSIBLE_TAMPERING
- All attempts (success and failure) are recorded in the audit trail

## Files Added
```
app/domain/entities/verification_result.py
app/domain/entities/verification_audit.py
app/application/ports/verification_audit_repository.py
app/application/use_cases/verification_dto.py
app/application/use_cases/verify_qr_token_use_case.py
app/application/use_cases/get_verification_history_use_case.py
app/infrastructure/persistence/verification_audit_mapper.py
app/infrastructure/persistence/dynamodb_verification_audit_repository.py
app/api/schemas/verification_schemas.py
app/api/routers/verify.py
tests/fakes/fake_verification_audit_repository.py
tests/unit/domain/test_verification.py
tests/unit/application/test_verify_qr_token_use_case.py
tests/unit/application/test_get_verification_history_use_case.py
tests/unit/infrastructure/test_verification_audit_mapper.py
tests/integration/test_verification_api.py
```

## Files Modified
```
app/container.py   — added verification_audit_repository, verify_qr_token_use_case, get_verification_history_use_case
app/main.py        — registered verify router
```

## DynamoDB Items
| Entity | PK | SK |
|--------|----|----|
| VerificationAudit | QR#{token} | AUDIT#{iso_timestamp} |

Audit entries use the same PK as the QRToken (QR#{token}) with a sort key prefixed by AUDIT#, enabling efficient query of all scan attempts for a given token.

## Test Coverage
- Domain: 8 tests (VerificationResult factory methods, VerificationAuditEntry creation)
- Use cases: 6 + 3 = 9 tests (verify flow, history retrieval)
- Infrastructure: 3 mapper roundtrip tests
- Integration: 3 API tests
- Total: 23 new tests

## Integration with Phase 5A
- Verification reads QRToken via HealthCardRepository.get_qr_token()
- Consumption via HealthCardRepository.consume_qr_token()
- No duplicate QRToken storage — single source of truth from Phase 5A

## Handoff
- Phase 5 (A+B) is complete: Health Cards + QR + Verification + Tamper Detection
- Next phase: SNS buyer notifications, PreventIQ, or Flywheel Dashboard
- 352 total tests passing, ruff clean, mypy clean
