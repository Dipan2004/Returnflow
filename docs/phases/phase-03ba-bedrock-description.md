# Phase 3Ba — Bedrock Damage Description Layer

## Objective
Replace the rule-based `describe_damage` stub from Phase 3A with a production Bedrock Claude Haiku adapter behind a clean `DescriptionGenerationPort`. The `GradingPort` contract is simplified: `grade_images` now returns `damage_description` directly inside `GradingResult`, eliminating the separate `describe_damage` call.

## Scope
- `DescriptionGenerationPort` — new port
- `BedrockDescriptionAdapter` — Claude Haiku integration with retry + fallback
- `prompt_templates.py` — deterministic prompt construction
- `response_parser.py` — response parsing, 25-word validation, truncation
- `RekognitionGradingAdapter` — inject `DescriptionGenerationPort`, remove rule-based stub
- `GradingPort` — remove `describe_damage`, add `damage_description` + `description_used_fallback` to `GradingResult`
- `ProcessGradingUseCase` — remove `describe_damage` call (description now in `GradingResult`)
- `Container` — register `bedrock_client`, `description_adapter`, inject into `grading_adapter`
- `clients.py` — add `build_bedrock_client`
- `pyproject.toml` — add `boto3-stubs[bedrock-runtime]`

## Files Added
```
app/application/ports/description_generation_port.py
app/infrastructure/adapters/bedrock/__init__.py
app/infrastructure/adapters/bedrock/prompt_templates.py
app/infrastructure/adapters/bedrock/response_parser.py
app/infrastructure/adapters/bedrock/bedrock_description_adapter.py
tests/fakes/fake_description_generation_port.py
tests/unit/infrastructure/test_response_parser.py
tests/unit/infrastructure/test_prompt_templates.py
tests/unit/infrastructure/test_bedrock_description_adapter.py
docs/phases/phase-03ba-bedrock-description.md
```

## Files Modified
```
app/application/ports/grading_port.py          — removed describe_damage; GradingResult gains damage_description + description_used_fallback
app/infrastructure/adapters/grading/rekognition_adapter.py — inject DescriptionGenerationPort; remove _build_description stub
app/application/use_cases/process_grading_use_case.py     — remove describe_damage call
app/infrastructure/aws/clients.py              — add build_bedrock_client
app/container.py                               — register bedrock_client, description_adapter
tests/fakes/fake_grading_port.py               — updated to new GradingResult shape
pyproject.toml                                 — add boto3-stubs[bedrock-runtime]
```

## Architecture Decisions
- `DescriptionGenerationPort` is a separate port from `GradingPort`. Bedrock is a different infrastructure concern from Rekognition. Keeps adapters independently testable and swappable.
- Description is generated inside `RekognitionGradingAdapter.grade_images` — result is one coherent `GradingResult`. No two-step call in the use case layer.
- Fallback descriptions are grade-specific plain strings — never fail silently with empty string.
- Retry: 2 attempts with 0.5s * attempt backoff — handles transient Bedrock throttling.
- 25-word limit enforced in `validate_description` via truncation — never raises on long responses, always returns valid output.
- Prompt is deterministic: sorted by confidence descending, fixed template. Same input = same prompt every time.

## Test Coverage
- `test_response_parser.py` — 9 cases: valid parse, missing period, quote stripping, invalid JSON, empty content, missing content key, truncation, too-short raises, word count
- `test_prompt_templates.py` — 5 cases: word limit in system prompt, buyer perspective, no-damage prompt, with-labels prompt, sort order
- `test_bedrock_description_adapter.py` — 5 cases: no-labels shortcut, successful generation, fallback on ClientError, retry then succeed, word count in response

## Remaining Work — Phase 3Bb
- `HumanReviewRequest` entity
- SQS adapter + `HumanReviewQueuePort`
- `ProcessGradingUseCase` dispatches to SQS when `requires_review=True`
- Step Functions Express Workflow: GradeImages → CheckConfidence → GenerateDamageDescription → SendToHumanReview states
- `WorkflowOrchestrationService`
- `GET /grades/{return_id}/workflow` endpoint
- `GET /grades/{return_id}/review-status` endpoint

## Handoff Instructions
1. Load `docs/PROJECT_STATE.md`, `docs/REPOSITORY_MAP.md`, this file.
2. All Phase 3Ba files are in the repo — run `pytest tests/unit/infrastructure/` to verify passing.
3. Phase 3Bb entry point: implement `HumanReviewQueuePort` in `app/application/ports/human_review_queue_port.py`, then SQS adapter in `app/infrastructure/adapters/sqs/`.
4. `ProcessGradingUseCase` needs one new constructor arg: `human_review_queue_port: HumanReviewQueuePort`.