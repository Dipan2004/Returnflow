# app/infrastructure/persistence/dynamodb_outcome_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.outcome_repository import OutcomeRepository
from app.domain.entities.disposition_outcome import DispositionOutcome
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.outcome_mapper import (
    from_item,
    outcome_pk,
    outcome_sk,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBOutcomeRepository(OutcomeRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, outcome: DispositionOutcome) -> None:
        item = to_item(outcome)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_return_id(self, return_id: ReturnId) -> DispositionOutcome | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={"PK": outcome_pk(return_id), "SK": outcome_sk()},
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)
