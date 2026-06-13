# app/infrastructure/persistence/dynamodb_condition_grade_repository.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.condition_grade_repository import ConditionGradeRepository
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.condition_grade_mapper import (
    condition_grade_pk,
    condition_grade_sk,
    from_item,
    to_item,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class DynamoDBConditionGradeRepository(ConditionGradeRepository):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def save(self, condition_grade: ConditionGrade) -> None:
        item = to_item(condition_grade)
        try:
            await asyncio.to_thread(self._table.put_item, Item=item)
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

    async def get_by_return_id(self, return_id: ReturnId) -> ConditionGrade | None:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={
                    "PK": condition_grade_pk(return_id),
                    "SK": condition_grade_sk(),
                },
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

        item = response.get("Item")
        if item is None:
            return None
        return from_item(item)