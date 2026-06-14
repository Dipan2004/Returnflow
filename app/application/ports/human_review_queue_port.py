# app/application/ports/human_review_queue_port.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.human_review_request import HumanReviewRequest


@dataclass(frozen=True)
class QueuePublishResult:
    message_id: str
    queue_url: str
    success: bool


class HumanReviewQueuePort(ABC):
    @abstractmethod
    async def publish(self, review_request: HumanReviewRequest) -> QueuePublishResult: ...
