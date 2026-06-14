# tests/fakes/fake_human_review_queue_port.py
from __future__ import annotations

import uuid

from app.application.ports.human_review_queue_port import HumanReviewQueuePort, QueuePublishResult
from app.domain.entities.human_review_request import HumanReviewRequest


class FakeHumanReviewQueuePort(HumanReviewQueuePort):
    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail
        self.published: list[HumanReviewRequest] = []

    async def publish(self, review_request: HumanReviewRequest) -> QueuePublishResult:
        if self._should_fail:
            from app.domain.exceptions import InfrastructureError

            raise InfrastructureError("SQS", "Fake SQS failure")
        self.published.append(review_request)
        return QueuePublishResult(
            message_id=str(uuid.uuid4()),
            queue_url="https://sqs.ap-south-1.amazonaws.com/123456789012/fake-queue",
            success=True,
        )
