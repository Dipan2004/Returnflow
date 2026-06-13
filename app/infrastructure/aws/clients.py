from __future__ import annotations

from typing import TYPE_CHECKING

import boto3

from app.config import AppConfig

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_s3.client import S3Client


def build_dynamodb_table(config: AppConfig) -> Table:
    resource = boto3.resource(
        "dynamodb",
        region_name=config.aws_region,
        endpoint_url=config.dynamodb_endpoint_url,
    )
    return resource.Table(config.dynamodb_table_name)


def build_s3_client(config: AppConfig) -> S3Client:
    return boto3.client(
        "s3",
        region_name=config.aws_region,
        endpoint_url=config.s3_endpoint_url,
    )

