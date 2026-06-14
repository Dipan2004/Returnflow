# app/infrastructure/persistence/dynamodb_verification_audit_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.verification_audit_repository import VerificationAuditRepository
from app.domain.entities.verification_audit import VerificationAuditEntry
from app.domain.exceptions import InfrastructureError
from app.infrastructure.persistence.verification_audit_mapper import (
    audit_pk,
    from_item,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBVerificationAuditRepository(VerificationAuditRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, entry: VerificationAuditEntry) -> None:
        item = to_item(entry)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_history(self, qr_token: str) -> list[VerificationAuditEntry]:
        try:
            response = await asyncio.to_thread(
                self._table.query,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
                ExpressionAttributeValues={
                    ":pk": audit_pk(qr_token),
                    ":prefix": "AUDIT#",
                },
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc
        return [from_item(item) for item in response.get("Items", [])]
