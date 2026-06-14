# tests/fakes/fake_fraud_history_port.py
from __future__ import annotations

from app.application.ports.fraud_history_port import BuyerFraudHistory, FraudHistoryPort


class FakeFraudHistoryPort(FraudHistoryPort):
    def __init__(
        self,
        total_returns: int = 0,
        high_value_returns: int = 0,
        same_sku_returns: int = 0,
        returns_last_24h: int = 0,
    ) -> None:
        self._total = total_returns
        self._high_value = high_value_returns
        self._same_sku = same_sku_returns
        self._last_24h = returns_last_24h
        self._overrides: dict[str, BuyerFraudHistory] = {}

    def set_history(
        self,
        buyer_id: str,
        total_returns: int = 0,
        high_value_returns: int = 0,
        same_sku_returns: int = 0,
        returns_last_24h: int = 0,
    ) -> None:
        self._overrides[buyer_id] = BuyerFraudHistory(
            buyer_id=buyer_id,
            total_returns_in_window=total_returns,
            high_value_returns_in_window=high_value_returns,
            same_sku_returns_in_window=same_sku_returns,
            returns_last_24h=returns_last_24h,
        )

    async def get_buyer_history(
        self,
        buyer_id: str,
        sku_id: str,
        window_hours: int,
    ) -> BuyerFraudHistory:
        if buyer_id in self._overrides:
            return self._overrides[buyer_id]
        return BuyerFraudHistory(
            buyer_id=buyer_id,
            total_returns_in_window=self._total,
            high_value_returns_in_window=self._high_value,
            same_sku_returns_in_window=self._same_sku,
            returns_last_24h=self._last_24h,
        )
