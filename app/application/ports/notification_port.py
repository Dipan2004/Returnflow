from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BuyerNotificationPayload:
    buyer_id: str
    return_id: str
    sku_id: str
    grade: str
    damage_description: str
    recovery_value: Decimal
    mrp: Decimal
    distance_km: float
    accept_url: str


@dataclass(frozen=True)
class NotificationResult:
    message_id: str
    channel: str
    delivered: bool


class NotificationPort(ABC):
    @abstractmethod
    async def notify_buyer(
        self,
        payload: BuyerNotificationPayload,
    ) -> NotificationResult: ...

    @abstractmethod
    async def notify_human_review(
        self,
        return_id: str,
        reason: str,
        confidence: float,
    ) -> NotificationResult: ...