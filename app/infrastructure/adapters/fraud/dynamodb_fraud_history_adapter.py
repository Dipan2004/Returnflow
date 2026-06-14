# app/infrastructure/adapters/fraud/dynamodb_fraud_history_adapter.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from botocore.exceptions import ClientError

from app.application.ports.fraud_history_port import BuyerFraudHistory, FraudHistoryPort
from app.domain.exceptions import InfrastructureError

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


def _safe_int(value: Any) -> int:
    if value is None:
        return 0
    return int(value)


class DynamoDBFraudHistoryAdapter(FraudHistoryPort):
    def __init__(self, table: Table) -> None:
        self._table = table

    async def get_buyer_history(
        self,
        buyer_id: str,
        sku_id: str,
        window_hours: int,
    ) -> BuyerFraudHistory:
        try:
            response = await asyncio.to_thread(
                self._table.get_item,
                Key={
                    "PK": f"FRAUD#{buyer_id}",
                    "SK": f"SKU#{sku_id}",
                },
            )
        except ClientError as exc:
            raise InfrastructureError("DynamoDB", str(exc)) from exc

        item = response.get("Item")
        if item is None:
            return BuyerFraudHistory(
                buyer_id=buyer_id,
                total_returns_in_window=0,
                high_value_returns_in_window=0,
                same_sku_returns_in_window=0,
                returns_last_24h=0,
            )

        return BuyerFraudHistory(
            buyer_id=buyer_id,
            total_returns_in_window=_safe_int(item.get("total_returns_in_window")),
            high_value_returns_in_window=_safe_int(item.get("high_value_returns_in_window")),
            same_sku_returns_in_window=_safe_int(item.get("same_sku_returns_in_window")),
            returns_last_24h=_safe_int(item.get("returns_last_24h")),
        )
