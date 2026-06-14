# app/infrastructure/persistence/dynamodb_buyer_match_repository.py | 48 lines
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.buyer_match_repository import BuyerMatchRepository
from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.buyer_match_mapper import (
    buyer_match_pk,
    buyer_match_sk,
    from_item,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBBuyerMatchRepository(BuyerMatchRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, result: BuyerMatchResult) -> None:
        item = to_item(result)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_return_id(self, return_id: ReturnId) -> BuyerMatchResult | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={
                    "PK": buyer_match_pk(return_id),
                    "SK": buyer_match_sk(),
                },
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)