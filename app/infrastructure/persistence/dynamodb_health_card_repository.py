# app/infrastructure/persistence/dynamodb_health_card_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.health_card_repository import HealthCardRepository
from app.domain.entities.health_card import HealthCard
from app.domain.entities.qr_token import QRToken
from app.domain.exceptions import InfrastructureError, QRTokenNotFoundError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.health_card_mapper import (
    from_item as hc_from_item,
)
from app.infrastructure.persistence.health_card_mapper import (
    health_card_pk,
    health_card_sk,
)
from app.infrastructure.persistence.health_card_mapper import (
    to_item as hc_to_item,
)
from app.infrastructure.persistence.qr_token_mapper import (
    from_item as qr_from_item,
)
from app.infrastructure.persistence.qr_token_mapper import (
    qr_token_pk,
    qr_token_sk,
)
from app.infrastructure.persistence.qr_token_mapper import (
    to_item as qr_to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBHealthCardRepository(HealthCardRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, health_card: HealthCard) -> None:
        item = hc_to_item(health_card)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_return_id(self, return_id: ReturnId) -> HealthCard | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={"PK": health_card_pk(return_id), "SK": health_card_sk()},
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        item = response.get("Item")
        if item is None:
            return None
        return hc_from_item(item)

    async def save_qr_token(self, qr_token: QRToken) -> None:
        item = qr_to_item(qr_token)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_qr_token(self, token: str) -> QRToken | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={"PK": qr_token_pk(token), "SK": qr_token_sk()},
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        item = response.get("Item")
        if item is None:
            return None
        return qr_from_item(item)

    async def consume_qr_token(self, token: str, agent_id: str) -> QRToken:
        qr = await self.get_qr_token(token)
        if qr is None:
            raise QRTokenNotFoundError(token)
        qr.consume(agent_id)
        await self.save_qr_token(qr)
        return qr
