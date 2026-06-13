from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.return_repository import ReturnRepository
from app.domain.entities.return_request import ReturnRequest
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.return_item_mapper import (
    buyer_gsi_pk,
    from_item,
    return_request_pk,
    return_request_sk,
    seller_gsi_pk,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

SELLER_INDEX = "seller-index"
BUYER_INDEX = "buyer-index"


class DynamoDBReturnRepository(ReturnRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, return_request: ReturnRequest) -> None:
        item = to_item(return_request)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_id(self, return_id: ReturnId) -> ReturnRequest | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={"PK": return_request_pk(return_id), "SK": return_request_sk()},
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)

    async def get_by_seller(self, seller_id: str, limit: int = 50) -> list[ReturnRequest]:
        try:
            response = await asyncio.to_thread(
                self._table.query,
                IndexName=SELLER_INDEX,
                KeyConditionExpression="GSI1PK = :pk",
                ExpressionAttributeValues={":pk": seller_gsi_pk(seller_id)},
                ScanIndexForward=False,
                Limit=limit,
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

        return [from_item(item) for item in response.get("Items", [])]

    async def get_by_buyer(self, buyer_id: str, limit: int = 50) -> list[ReturnRequest]:
        try:
            response = await asyncio.to_thread(
                self._table.query,
                IndexName=BUYER_INDEX,
                KeyConditionExpression="GSI2PK = :pk",
                ExpressionAttributeValues={":pk": buyer_gsi_pk(buyer_id)},
                ScanIndexForward=False,
                Limit=limit,
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

        return [from_item(item) for item in response.get("Items", [])]
