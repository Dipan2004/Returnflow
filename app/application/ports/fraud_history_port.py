# app/application/ports/fraud_history_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BuyerFraudHistory:
    buyer_id: str
    total_returns_in_window: int
    high_value_returns_in_window: int
    same_sku_returns_in_window: int
    returns_last_24h: int


class FraudHistoryPort(ABC):
    @abstractmethod
    async def get_buyer_history(
        self,
        buyer_id: str,
        sku_id: str,
        window_hours: int,
    ) -> BuyerFraudHistory: ...
