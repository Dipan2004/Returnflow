# app/infrastructure/adapters/fraud/in_memory_fraud_history_adapter.py
from __future__ import annotations

from app.application.ports.fraud_history_port import BuyerFraudHistory, FraudHistoryPort


class InMemoryFraudHistoryAdapter(FraudHistoryPort):
    async def get_buyer_history(
        self,
        buyer_id: str,
        sku_id: str,
        window_hours: int,
    ) -> BuyerFraudHistory:
        return BuyerFraudHistory(
            buyer_id=buyer_id,
            total_returns_in_window=0,
            high_value_returns_in_window=0,
            same_sku_returns_in_window=0,
            returns_last_24h=0,
        )
