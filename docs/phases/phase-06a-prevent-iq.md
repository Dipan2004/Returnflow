# Phase 6A — PreventIQ (SageMaker + Return Prediction)

## Objective
Implement PreventIQ — the purchase-time intelligence layer that predicts return probability
and recommends optimal sizes before checkout, reducing returns at the source.

## What Was Built
- ReturnPrediction entity + ReturnProbability, KeepRate, SizeRisk value objects
- SizeRecommendation entity
- PreventIQEngine domain service (feature interpretation, risk categorization, size logic)
- PredictionModelPort, BuyerFeaturePort, SkuFeaturePort application ports
- DemoPredictionModel (deterministic weighted model for demo)
- SageMakerPredictionAdapter (production path with fallback handling)
- InMemoryBuyerFeatures + InMemorySkuFeatures adapters
- PredictReturnUseCase + GetSizeRecommendationUseCase
- API: GET /prevent-iq/predict-return, GET /prevent-iq/size-recommendation

## Prediction Model
Deterministic formula: `return_rate * 0.4 + category_rate * 0.3 + size_mismatch * 0.3`
- LOW risk: < 20% return probability
- MEDIUM risk: 20-50%
- HIGH risk: > 50%
- Size warning triggered when mismatch_rate > 25%

## SageMaker Integration
- `SageMakerPredictionAdapter` uses `boto3.client("sagemaker-runtime").invoke_endpoint()`
- Handles: endpoint unavailable, timeout, malformed responses
- Falls back to 0.15 (category average) on any failure
- Container uses DemoPredictionModel for local dev, swappable to SageMaker

## Files Added (31)
Domain: 6 files (entities, value objects, service)
Application: 6 files (ports, DTOs, use cases)
Infrastructure: 6 files (adapters for prediction, features)
API: 2 files (schemas, router)
Test fakes: 3 files
Tests: 7 files (87 new tests)
Documentation: 1 file

## Files Modified (4)
- app/infrastructure/aws/clients.py — added build_sagemaker_runtime_client
- app/container.py — registered all PreventIQ providers
- app/main.py — registered predict router
- app/application/ports/prediction_port.py — replaced with PredictionModelPort re-export

## Test Coverage
- Domain: 48 tests (value objects, entities, engine logic)
- Application: 14 use case tests
- Infrastructure: 17 tests (demo model, sagemaker adapter)
- Integration: 8 API tests
- Total: 87 new tests, 464 total passing

## Handoff
- Phase 6A complete
- PreventIQ serves predictions at purchase time via GET /prevent-iq/predict-return
- SageMaker adapter ready for production endpoint deployment
- Next: Phase 6B (Flywheel Dashboard + Metrics Aggregation)
