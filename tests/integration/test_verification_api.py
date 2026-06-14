# tests/integration/test_verification_api.py
from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch

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
        sqs = boto3.client("sqs", region_name=config.aws_region)
        queue_response = sqs.create_queue(QueueName="returniq-human-review")
        queue_url = queue_response["QueueUrl"]
        with (
            patch.dict("os.environ", {"SQS_HUMAN_REVIEW_QUEUE_URL": queue_url}),
            TestClient(app) as test_client,
        ):
            yield test_client


def test_verify_unknown_token(client: TestClient) -> None:
    resp = client.get("/verify/unknown_tok_xxxxxxxxxxxxxxxxx?agent_id=agent_1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert data["status"] == "NOT_FOUND"


def test_verify_missing_agent_id(client: TestClient) -> None:
    resp = client.get("/verify/some_token")
    assert resp.status_code == 422


def test_history_empty(client: TestClient) -> None:
    resp = client.get("/verify/unknown_tok/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_scans"] == 0
