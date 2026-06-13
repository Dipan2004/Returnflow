from __future__ import annotations

from abc import ABC, abstractmethod


class FraudPort(ABC):
    @abstractmethod
    async def get_purchase_count_in_window(
        self,
        buyer_id: str,
        sku_id: str,
        window_hours: int,
    ) -> int: ...

    @abstractmethod
    async def record_fraud_flag(
        self,
        buyer_id: str,
        sku_id: str,
        reason: str,
    ) -> None: ...