# app/infrastructure/aws/clients.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import boto3

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_rekognition import RekognitionClient
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sagemaker_runtime import SageMakerRuntimeClient
    from mypy_boto3_sqs import SQSClient

    from app.config import AppConfig


def build_dynamodb_table(config: AppConfig) -> Table | None:
    if config.demo_mode:
        return None
    kwargs: dict[str, Any] = {"region_name": config.aws_region}
    if config.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = config.dynamodb_endpoint_url
    try:
        resource = boto3.resource("dynamodb", **kwargs)
        table = resource.Table(config.dynamodb_table_name)
        if config.is_local:
            try:
                table.load()
            except resource.meta.client.exceptions.ResourceNotFoundException:
                table = resource.create_table(
                    TableName=config.dynamodb_table_name,
                    KeySchema=[
                        {"AttributeName": "PK", "KeyType": "HASH"},
                        {"AttributeName": "SK", "KeyType": "RANGE"},
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "PK", "AttributeType": "S"},
                        {"AttributeName": "SK", "AttributeType": "S"},
                    ],
                    BillingMode="PAY_PER_REQUEST",
                )
                table.wait_until_exists()
        return table
    except Exception:
        return None


def build_s3_client(config: AppConfig) -> S3Client | None:
    if config.demo_mode:
        return None
    kwargs: dict[str, Any] = {"region_name": config.aws_region}
    if config.s3_endpoint_url:
        kwargs["endpoint_url"] = config.s3_endpoint_url
    try:
        return boto3.client("s3", **kwargs)
    except Exception:
        return None


def build_rekognition_client(config: AppConfig) -> RekognitionClient | None:
    if config.demo_mode:
        return None
    try:
        return boto3.client("rekognition", region_name=config.aws_region)
    except Exception:
        return None


def build_bedrock_client(config: AppConfig) -> BedrockRuntimeClient | None:
    if config.demo_mode:
        return None
    try:
        return boto3.client("bedrock-runtime", region_name=config.bedrock_region)
    except Exception:
        return None


def build_sqs_client(config: AppConfig) -> SQSClient | None:
    if config.demo_mode:
        return None
    kwargs: dict[str, Any] = {"region_name": config.aws_region}
    if config.sqs_endpoint_url:
        kwargs["endpoint_url"] = config.sqs_endpoint_url
    try:
        return boto3.client("sqs", **kwargs)
    except Exception:
        return None


def build_sagemaker_runtime_client(config: AppConfig) -> SageMakerRuntimeClient | None:
    if config.demo_mode:
        return None
    try:
        return boto3.client("sagemaker-runtime", region_name=config.aws_region)
    except Exception:
        return None
