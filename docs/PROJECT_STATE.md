# Project State

_Last updated: end of Phase 5B — QR Verification + Tamper Detection._

## Summary

ReturnIQ backend is a Clean Architecture / DDD FastAPI service. The complete
returns pipeline is implemented: condition grading, damage description,
disposition routing, fraud detection, buyer matching, health card generation,
QR token issuance, and tamper-evident verification.

## Phase History

| Phase | Description | Status |
|---|---|---|
| 1 | Domain Foundation | ✅ Complete |
| 2 | Return Intake APIs | ✅ Complete |
| 3A | Condition Grading (Rekognition) | ✅ Complete |
| 3Ba | Bedrock Damage Description | ✅ Complete |
| 3Bb | Workflow + Human Review Queue | ✅ Complete |
| 4A | Disposition Engine | ✅ Complete |
| 4B | Fraud Detection Engine | ✅ Complete |
| 4C | Buyer Matching | ✅ Complete |
| 4D | Routing Orchestration | ✅ Complete |
| 5A | Health Card + QR Generation | ✅ Complete |
| 5B | QR Verification + Tamper Detection | ✅ Complete |
| 6 | SNS Notifications + PreventIQ | 🔜 Next |

## Current Validation

- **352 tests passing**
- ruff check: PASS
- mypy app: PASS (159 source files)

## API Endpoints

| Method | Path | Phase |
|--------|------|-------|
| GET | /health | 1 |
| POST | /returns | 2 |
| GET | /returns/{id} | 2 |
| GET | /returns/{id}/status | 2 |
| POST | /returns/{id}/images/complete | 2 |
| POST | /grades | 3A |
| POST | /grades/process | 3Bb |
| GET | /grades/{id} | 3A |
| GET | /grades/{id}/workflow | 3Bb |
| GET | /grades/{id}/review-status | 3Bb |
| POST | /dispositions/calculate | 4A |
| POST | /dispositions/calculate/{return_id} | 4D |
| GET | /dispositions/{id} | 4A |
| POST | /fraud/assess | 4B |
| GET | /fraud/{id} | 4B |
| POST | /buyer-match/compute | 4C |
| GET | /buyer-match/{id} | 4C |
| POST | /health-cards/generate/{return_id} | 5A |
| GET | /health-cards/{id} | 5A |
| GET | /health-cards/by-qr/{token} | 5A |
| GET | /verify/{qr_token} | 5B |
| GET | /verify/{qr_token}/history | 5B |

## What Is NOT Implemented Yet

- SNS/SES Buyer Notifications
- SageMaker PreventIQ (return prediction)
- Flywheel Dashboard APIs
- Step Functions ASL template
- Authentication (API key / Cognito)

## How To Run

```bash
pip install -e ".[dev]"
docker compose up -d
cp .env.example .env
uvicorn app.main:app --reload --port 8000
pytest tests/
ruff check .
mypy app --ignore-missing-imports
```
