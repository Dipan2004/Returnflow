# tests/integration/test_buyer_match_api.py | 120 lines
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


class TestComputeBuyerMatchAPI:
    def test_grade_a_returns_200(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID001", "sku_id": "SKU001", "pincode": "110001", "grade": "A"},
        )
        assert resp.status_code == 200

    def test_grade_a_match_found(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID002", "sku_id": "SKU001", "pincode": "110001", "grade": "A"},
        )
        data = resp.json()
        assert data["match_found"] is True
        assert data["p2p_recommended"] is True
        assert data["eligibility"] == "ELIGIBLE"

    def test_grade_c_not_eligible(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID003", "sku_id": "SKU001", "pincode": "110001", "grade": "C"},
        )
        data = resp.json()
        assert data["match_found"] is False
        assert data["eligibility"] == "NOT_ELIGIBLE"

    def test_sku001_demand_85(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID004", "sku_id": "SKU001", "pincode": "110001", "grade": "A"},
        )
        data = resp.json()
        assert data["demand_score"] == 85
        assert data["demand_level"] == "HIGH"

    def test_sku003_low_demand(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID005", "sku_id": "SKU003", "pincode": "110001", "grade": "A"},
        )
        data = resp.json()
        assert data["demand_score"] == 25
        assert data["demand_level"] == "LOW"

    def test_invalid_grade_422(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID006", "sku_id": "SKU001", "pincode": "110001", "grade": "Z"},
        )
        assert resp.status_code == 422

    def test_response_has_all_fields(self, client: TestClient) -> None:
        resp = client.post(
            "/buyer-match/compute",
            json={"return_id": "RID007", "sku_id": "SKU001", "pincode": "110001", "grade": "A"},
        )
        data = resp.json()
        for field in [
            "return_id", "sku_id", "pincode", "grade", "demand_score", "demand_level",
            "estimated_buyers", "match_found", "eligibility", "confidence", "p2p_recommended",
            "computed_at",
        ]:
            assert field in data, f"missing field: {field}"


class TestGetBuyerMatchAPI:
    def test_get_after_compute(self, client: TestClient) -> None:
        client.post(
            "/buyer-match/compute",
            json={"return_id": "RID010", "sku_id": "SKU001", "pincode": "110001", "grade": "A"},
        )
        resp = client.get("/buyer-match/RID010")
        assert resp.status_code == 200
        assert resp.json()["return_id"] == "RID010"

    def test_get_not_found_404(self, client: TestClient) -> None:
        resp = client.get("/buyer-match/NONEXISTENT999")
        assert resp.status_code == 404

    def test_get_returns_persisted_data(self, client: TestClient) -> None:
        client.post(
            "/buyer-match/compute",
            json={"return_id": "RID011", "sku_id": "SKU002", "pincode": "400001", "grade": "A"},
        )
        resp = client.get("/buyer-match/RID011")
        data = resp.json()
        assert data["sku_id"] == "SKU002"
        assert data["demand_score"] == 72