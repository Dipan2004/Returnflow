# tests/integration/test_predict_api.py
from __future__ import annotations

from collections.abc import Iterator

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.config import get_config
from app.main import app


@pytest.fixture
def aws_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture
def client(aws_credentials: None) -> Iterator[TestClient]:
    config = get_config()

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=config.aws_region)
        dynamodb.create_table(
            TableName=config.dynamodb_table_name,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
                {"AttributeName": "GSI2PK", "AttributeType": "S"},
                {"AttributeName": "GSI2SK", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "seller-index",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "buyer-index",
                    "KeySchema": [
                        {"AttributeName": "GSI2PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI2SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
        )

        s3 = boto3.client("s3", region_name=config.aws_region)
        s3.create_bucket(
            Bucket=config.s3_image_bucket,
            CreateBucketConfiguration={"LocationConstraint": config.aws_region},
        )

        with TestClient(app) as test_client:
            yield test_client


class TestPredictReturnAPI:
    def test_predict_return_200(self, client: TestClient) -> None:
        resp = client.get(
            "/prevent-iq/predict-return",
            params={"buyer_id": "BUYER001", "sku_id": "SKU001", "size": "M"},
        )
        assert resp.status_code == 200

    def test_predict_return_has_fields(self, client: TestClient) -> None:
        resp = client.get(
            "/prevent-iq/predict-return",
            params={"buyer_id": "BUYER001", "sku_id": "SKU001", "size": "M"},
        )
        data = resp.json()
        for field in [
            "return_probability",
            "risk_level",
            "keep_rate",
            "recommended_size",
            "size_warning",
            "category_avg_return_rate",
        ]:
            assert field in data, f"missing field: {field}"

    def test_predict_return_high_risk_buyer(self, client: TestClient) -> None:
        resp = client.get(
            "/prevent-iq/predict-return",
            params={"buyer_id": "BUYER002", "sku_id": "SKU003", "size": "XL"},
        )
        data = resp.json()
        assert data["risk_level"] in ("MEDIUM", "HIGH")
        assert data["return_probability"] >= 0.2

    def test_predict_return_missing_params_422(self, client: TestClient) -> None:
        resp = client.get("/prevent-iq/predict-return", params={"buyer_id": "B1"})
        assert resp.status_code == 422


class TestSizeRecommendationAPI:
    def test_size_recommendation_200(self, client: TestClient) -> None:
        resp = client.get(
            "/prevent-iq/size-recommendation",
            params={"sku_id": "SKU001", "size": "L"},
        )
        assert resp.status_code == 200

    def test_size_recommendation_fields(self, client: TestClient) -> None:
        resp = client.get(
            "/prevent-iq/size-recommendation",
            params={"sku_id": "SKU001", "size": "L"},
        )
        data = resp.json()
        assert data["recommended_size"] == "M"
        assert "confidence" in data
        assert "mismatch_rate" in data

    def test_size_recommendation_missing_params(self, client: TestClient) -> None:
        resp = client.get("/prevent-iq/size-recommendation", params={"sku_id": "SKU001"})
        assert resp.status_code == 422

    def test_size_recommendation_with_brand(self, client: TestClient) -> None:
        resp = client.get(
            "/prevent-iq/size-recommendation",
            params={"sku_id": "SKU001", "size": "L", "brand": "BrandA"},
        )
        assert resp.status_code == 200
