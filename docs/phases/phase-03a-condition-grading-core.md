# Phase 3A — Condition Grading Core

## Objective
Implement the CV-based condition grading pipeline without Bedrock or Step Functions. Produce a persisted `ConditionGrade` aggregate with a human-review gate and expose grading REST endpoints.

## Scope
Phase 3A covers:
- Domain: `ConditionGrade`, `DamageLabel`, `ConfidenceScore`, `Grade` (all pre-existing from Phase 1 domain scaffold)
- Domain service: `ConfidenceGate` (new)
- Port: `ConditionGradeRepository` (new), `GradingPort` (pre-existing)
- Adapter: `RekognitionGradingAdapter`, `grade_mapper`, `models` (all new)
- Use cases: `ProcessGradingUseCase`, `GetConditionGradeUseCase` (new)
- Persistence: `DynamoDBConditionGradeRepository`, `condition_grade_mapper` (new)
- API: `GET /grades/{return_id}`, `POST /grades` (new)
- Tests: domain, mapper, use case, fakes (new)

## Files Added