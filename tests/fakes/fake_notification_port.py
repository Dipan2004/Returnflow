# tests/fakes/fake_notification_port.py
from __future__ import annotations

import uuid

from app.application.ports.notification_port import (
    BuyerNotificationPayload,
    NotificationPort,
    NotificationResult,
)


class FakeNotificationPort(NotificationPort):
    def __init__(self) -> None:
        self.buyer_notifications: list[BuyerNotificationPayload] = []
        self.review_notifications: list[tuple[str, str, float]] = []

    async def notify_buyer(self, payload: BuyerNotificationPayload) -> NotificationResult:
        self.buyer_notifications.append(payload)
        return NotificationResult(
            message_id=str(uuid.uuid4()), channel="FAKE", delivered=True
        )

    async def notify_human_review(
        self, return_id: str, reason: str, confidence: float
    ) -> NotificationResult:
        self.review_notifications.append((return_id, reason, confidence))
        return NotificationResult(
            message_id=str(uuid.uuid4()), channel="FAKE", delivered=True
        )
