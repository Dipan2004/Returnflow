# tests/integration/test_grades_api.py
from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.config import get_config
from app.main import app


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

        sqs = boto3.client("sqs", region_name=config.aws_region)
        queue_response = sqs.create_queue(QueueName="returniq-human-review")
        queue_url = queue_response["QueueUrl"]

        with patch.dict(
            "os.environ", {"SQS_HUMAN_REVIEW_QUEUE_URL": queue_url}
        ):
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def aws_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


def _create_return(client: TestClient) -> str:
    response = client.post(
        "/returns",
        json={
            "sku_id": "B08N5WRWNW",
            "seller_id": "seller_xyz",
            "buyer_id": "buyer_abc",
            "expected_image_count": 3,
        },
    )
    assert response.status_code == 201
    return response.json()["return_id"]


def test_get_condition_grade_not_found(client: TestClient) -> None:
    response = client.get("/grades/NONEXISTENT")
    assert response.status_code == 404


def test_get_workflow_state_not_found(client: TestClient) -> None:
    response = client.get("/grades/NONEXISTENT/workflow")
    assert response.status_code == 404


def test_get_review_status_not_found(client: TestClient) -> None:
    response = client.get("/grades/NONEXISTENT/review-status")
    assert response.status_code == 404
