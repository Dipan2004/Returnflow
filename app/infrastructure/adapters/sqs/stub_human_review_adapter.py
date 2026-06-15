# app/infrastructure/adapters/sqs/stub_human_review_adapter.py
from __future__ import annotations

from app.application.ports.human_review_queue_port import HumanReviewQueuePort, QueuePublishResult
from app.domain.entities.human_review_request import HumanReviewRequest


class StubHumanReviewAdapter(HumanReviewQueuePort):
    async def publish(self, review_request: HumanReviewRequest) -> QueuePublishResult:
        print(f"[DEMO] Human review request for return {review_request.return_id.value}")
        return QueuePublishResult(
            message_id="demo-msg-001",
            queue_url="demo://queue",
            success=True,
        )
