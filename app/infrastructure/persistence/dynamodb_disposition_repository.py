# app/infrastructure/persistence/dynamodb_disposition_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.disposition_repository import DispositionRepository
from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.disposition_mapper import (
    disposition_pk,
    disposition_sk,
    from_item,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBDispositionRepository(DispositionRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, decision: DispositionDecision) -> None:
        item = to_item(decision)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_return_id(self, return_id: ReturnId) -> DispositionDecision | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={
                    "PK": disposition_pk(return_id),
                    "SK": disposition_sk(),
                },
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)