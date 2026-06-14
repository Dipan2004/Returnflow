# app/infrastructure/adapters/sqs/sqs_human_review_adapter.py
from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from botocore.exceptions import ClientError

from app.application.ports.human_review_queue_port import HumanReviewQueuePort, QueuePublishResult
from app.domain.entities.human_review_request import HumanReviewRequest
from app.domain.exceptions import InfrastructureError
from app.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient

logger = get_logger(__name__)

_MAX_RETRIES = 2
_RETRY_DELAY_BASE = 0.5


class SQSHumanReviewAdapter(HumanReviewQueuePort):
    def __init__(
        self,
        sqs_client: SQSClient,
        queue_url: str,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._client = sqs_client
        self._queue_url = queue_url
        self._max_retries = max_retries

    async def publish(self, review_request: HumanReviewRequest) -> QueuePublishResult:
        payload = review_request.to_queue_payload()
        message_body = json.dumps(payload, default=str)
        message_attributes = self._build_message_attributes(review_request)

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._send_message(message_body, message_attributes)
                message_id = response["MessageId"]
                logger.info(
                    "Human review request published to SQS",
                    return_id=review_request.return_id.value,
                    message_id=message_id,
                    priority=review_request.priority.value,
                    attempt=attempt,
                )
                return QueuePublishResult(
                    message_id=message_id,
                    queue_url=self._queue_url,
                    success=True,
                )
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code", "Unknown")
                logger.warning(
                    "SQS publish attempt failed",
                    return_id=review_request.return_id.value,
                    error_code=error_code,
                    attempt=attempt,
                )
                if attempt == self._max_retries:
                    raise InfrastructureError(
                        "SQS", f"Failed to publish after {self._max_retries + 1} attempts: {exc}"
                    ) from exc
                await asyncio.sleep(_RETRY_DELAY_BASE * (attempt + 1))

        raise InfrastructureError("SQS", "Exhausted retries without success")

    async def _send_message(
        self,
        message_body: str,
        message_attributes: dict[str, Any],
    ) -> dict[str, Any]:
        response: dict[str, Any] = await asyncio.to_thread(
            self._client.send_message,
            QueueUrl=self._queue_url,
            MessageBody=message_body,
            MessageAttributes=message_attributes,
        )
        return response

    def _build_message_attributes(
        self, review_request: HumanReviewRequest
    ) -> dict[str, Any]:
        return {
            "ReturnId": {
                "DataType": "String",
                "StringValue": review_request.return_id.value,
            },
            "Priority": {
                "DataType": "String",
                "StringValue": review_request.priority.value,
            },
            "Confidence": {
                "DataType": "Number",
                "StringValue": str(review_request.confidence),
            },
        }
