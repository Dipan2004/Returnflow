# app/infrastructure/aws/clients.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import boto3

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_rekognition import RekognitionClient
    from mypy_boto3_s3 import S3Client

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