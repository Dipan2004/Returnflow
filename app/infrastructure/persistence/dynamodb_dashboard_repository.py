# app/infrastructure/persistence/dynamodb_dashboard_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.dashboard_repository import DashboardRepository
from app.domain.entities.dashboard_metrics import DashboardMetrics
from app.domain.exceptions import InfrastructureError
from app.infrastructure.persistence.dashboard_mapper import (
    dashboard_pk,
    dashboard_sk,
    from_item,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBDashboardRepository(DashboardRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, metrics: DashboardMetrics) -> None:
        item = to_item(metrics)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_latest(self, period: str) -> DashboardMetrics | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={"PK": dashboard_pk(), "SK": dashboard_sk(period)},
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)
