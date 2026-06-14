# app/infrastructure/persistence/dynamodb_fraud_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.fraud_repository import FraudRepository
from app.domain.entities.fraud_assessment import FraudAssessment
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.fraud_mapper import (
    fraud_pk,
    fraud_sk,
    from_item,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBFraudRepository(FraudRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, assessment: FraudAssessment) -> None:
        item = to_item(assessment)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_return_id(self, return_id: ReturnId) -> FraudAssessment | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={
                    "PK": fraud_pk(return_id),
                    "SK": fraud_sk(),
                },
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)
