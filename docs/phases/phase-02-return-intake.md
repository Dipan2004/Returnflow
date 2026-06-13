# Phase 2 — Return Intake APIs

## Objective

Deliver the Return Intake bounded context end to end: creating a return
request, issuing presigned S3 upload URLs, tracking lifecycle status, and
recording image upload completion — backed by DynamoDB and S3, behind a
Clean Architecture boundary with full dependency injection.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/returns` | Create a return request, returns presigned S3 PUT URLs |
| GET | `/returns/{return_id}` | Full return detail (status, image keys, parties) |
| GET | `/returns/{return_id}/status` | Lightweight lifecycle status |
| POST | `/returns/{return_id}/images/complete` | Confirm uploaded image keys, advance lifecycle |

## Architecture

```
app/api/routers/returns.py          FastAPI endpoints (DI via Provide[])
app/api/schemas/return_schemas.py   Request/response Pydantic models
app/application/use_cases/*         CreateReturn, GetReturn, GetReturnStatus,
                                     CompleteImageUpload
app/application/ports/*             ReturnRepository, ImageStoragePort (existing)
app/domain/entities/return_request.py  ReturnRequest aggregate (existing)
app/infrastructure/persistence/*    DynamoDB adapter + item mapper
app/infrastructure/storage/*        S3 presigned URL adapter
app/infrastructure/aws/clients.py   boto3 client/resource factories
app/container.py                    dependency-injector wiring
```

## DynamoDB Item Shape (`returniq-main`)

```
PK = RETURN#{return_id}      SK = REQUEST
GSI1PK = SELLER#{seller_id}  GSI1SK = RETURN#{created_at_iso}#{return_id}
GSI2PK = BUYER#{buyer_id}    GSI2SK = RETURN#{created_at_iso}#{return_id}

entity_type, return_id, sku_id, seller_id, buyer_id,
expected_image_count, status, image_keys[], created_at, updated_at
```

`seller-index` and `buyer-index` GSIs power `get_by_seller` /
`get_by_buyer` (used by future Health Card listing endpoints).

## S3 Key Convention

Presigned PUT URLs are issued for `pending/{return_id}/img_{NNN}.jpg`.
`CompleteImageUploadUseCase` verifies every submitted key:

1. Parses via `ImageKey.from_string` (validates prefix + extension).
2. Confirms `key.return_id == return_id` (rejects cross-tenant keys).
3. Confirms the object actually exists in S3 via `list_uploaded_keys`.

Only after all checks pass does it call `ReturnRequest.add_image_key`,
which transitions `AWAITING_IMAGES → IMAGES_RECEIVED` once
`expected_image_count` keys are present.

## Error Mapping

| Domain Exception | HTTP Status |
|---|---|
| `DomainValidationError` | 400 |
| `EntityNotFoundError` | 404 |
| `InvalidStateTransitionError` | 409 |
| `ImageUploadError` | 422 |
| `ConfidenceBelowThresholdError`, `FraudFlaggedError`, `QRToken*` | 409/404 (existing) |
| `InfrastructureError` | 502 |

## Dependency Injection

`Container` (dependency-injector) wires:

- `config` — `AppConfig` singleton (`get_config()`)
- `dynamodb_table` / `s3_client` — boto3 singletons built from config
- `return_repository` — `DynamoDBReturnRepository`
- `image_storage` — `S3ImageStorage`
- Use cases as `Factory` providers, injected via `Provide[Container.x]`
  into router handlers using `@inject`.

`app.main.create_app` wires the container against `app.api.routers`
during the FastAPI lifespan startup.

## Local Development

```bash
docker compose up -d            # dynamodb-local + dynamodb-admin
make dev                         # uvicorn with reload
```

`DYNAMODB_ENDPOINT_URL=http://localhost:8001` and `S3_ENDPOINT_URL`
(set in `.env`, copy from `.env.example`) point the adapters at local
infrastructure. For S3 locally, use a tool such as `localstack` or
point `S3_ENDPOINT_URL` at a MinIO instance; integration tests instead
use `moto` to mock both services in-process.

## Testing

- **Unit** (`tests/unit/application`): each use case tested against
  `FakeReturnRepository` / `FakeImageStorage` (in-memory fakes in
  `tests/fakes`). Covers happy paths, partial uploads, not-found,
  cross-tenant key rejection, and unseeded-upload rejection.
- **Integration** (`tests/integration/test_returns_api.py`): full
  FastAPI app over `moto`-mocked DynamoDB + S3, exercising all four
  endpoints including validation errors (422) and not-found (404).

Run: `make test`, `make test-unit`, `make test-integration`.

## Acceptance Criteria — Status

- [x] `POST /returns` creates a `ReturnRequest`, persists it, returns
      presigned upload URLs sized to `image_count`.
- [x] `GET /returns/{id}` returns full detail or 404.
- [x] `GET /returns/{id}/status` returns lifecycle status + image progress.
- [x] `POST /returns/{id}/images/complete` validates keys against S3 and
      the owning return, advances status when complete.
- [x] DynamoDB single-table adapter implements `ReturnRepository` fully
      (`save`, `get_by_id`, `get_by_seller`, `get_by_buyer`).
- [x] S3 adapter implements `ImageStoragePort` fully (`generate_upload_urls`,
      `generate_download_url`, `list_uploaded_keys`, `copy_to_graded`).
- [x] `mypy --strict` clean, `ruff check` clean, 18/18 tests passing.

## Out of Scope (Future Phases)

- Step Functions workflow trigger on `IMAGES_RECEIVED` (Phase 3).
- Rekognition grading, Bedrock description, router, fraud check (Phase 3).
- Health Card generation, QR issuance/verification (Phase 4).
- PreventIQ / SageMaker integration (Phase 5).
- Authentication/authorization (API key or Cognito) on API Gateway.
