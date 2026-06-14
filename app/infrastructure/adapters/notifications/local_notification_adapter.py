# app/infrastructure/adapters/notifications/local_notification_adapter.py
from __future__ import annotations

import uuid

from app.application.ports.notification_port import (
    BuyerNotificationPayload,
    NotificationPort,
    NotificationResult,
)
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class LocalNotificationAdapter(NotificationPort):
    def __init__(self) -> None:
        self._sent: list[BuyerNotificationPayload] = []

    async def notify_buyer(self, payload: BuyerNotificationPayload) -> NotificationResult:
        self._sent.append(payload)
        message_id = str(uuid.uuid4())
        logger.info(
            "Buyer notification sent (local)",
            buyer_id=payload.buyer_id,
            return_id=payload.return_id,
            message_id=message_id,
        )
        return NotificationResult(
            message_id=message_id, channel="LOCAL", delivered=True
        )

    async def notify_human_review(
        self, return_id: str, reason: str, confidence: float
    ) -> NotificationResult:
        message_id = str(uuid.uuid4())
        logger.info(
            "Human review notification (local)",
            return_id=return_id,
            reason=reason,
        )
        return NotificationResult(
            message_id=message_id, channel="LOCAL", delivered=True
        )
