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


def build_dynamodb_table(config: AppConfig) -> Table:
    kwargs: dict[str, Any] = {"region_name": config.aws_region}
    if config.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = config.dynamodb_endpoint_url
    resource = boto3.resource("dynamodb", **kwargs)
    return resource.Table(config.dynamodb_table_name)


def build_s3_client(config: AppConfig) -> S3Client:
    kwargs: dict[str, Any] = {"region_name": config.aws_region}
    if config.s3_endpoint_url:
        kwargs["endpoint_url"] = config.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def build_rekognition_client(config: AppConfig) -> RekognitionClient:
    return boto3.client("rekognition", region_name=config.aws_region)


def build_bedrock_client(config: AppConfig) -> BedrockRuntimeClient:
    return boto3.client("bedrock-runtime", region_name=config.bedrock_region)


def build_sqs_client(config: AppConfig) -> SQSClient:
    kwargs: dict[str, Any] = {"region_name": config.aws_region}
    if config.sqs_endpoint_url:
        kwargs["endpoint_url"] = config.sqs_endpoint_url
    return boto3.client("sqs", **kwargs)


def build_sagemaker_runtime_client(config: AppConfig) -> SageMakerRuntimeClient:
    return boto3.client("sagemaker-runtime", region_name=config.aws_region)