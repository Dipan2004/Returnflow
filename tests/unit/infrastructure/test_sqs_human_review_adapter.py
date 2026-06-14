# tests/unit/infrastructure/test_sqs_human_review_adapter.py
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.domain.entities.condition_grade import DamageLabel
from app.domain.entities.human_review_request import HumanReviewRequest
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.adapters.sqs.sqs_human_review_adapter import SQSHumanReviewAdapter


def _make_review_request(confidence: float = 72.0) -> HumanReviewRequest:
    return HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=confidence,
        threshold=87.0,
        damage_labels=[DamageLabel(name="Scratch", confidence=70.0)],
        image_keys=[ImageKey.pending("TEST123", 1)],
        reason="Confidence below threshold",
    )


def _make_client(message_id: str = "msg-123") -> MagicMock:
    client = MagicMock()
    client.send_message.return_value = {"MessageId": message_id}
    return client


def _make_adapter(
    client: MagicMock, max_retries: int = 2
) -> SQSHumanReviewAdapter:
    return SQSHumanReviewAdapter(
        sqs_client=client,
        queue_url="https://sqs.ap-south-1.amazonaws.com/123456789012/returniq-human-review",
        max_retries=max_retries,
    )


@pytest.mark.asyncio
async def test_publish_success() -> None:
    client = _make_client("msg-abc")
    adapter = _make_adapter(client)
    request = _make_review_request()

    result = await adapter.publish(request)

    assert result.success
    assert result.message_id == "msg-abc"
    client.send_message.assert_called_once()
    call_kwargs = client.send_message.call_args[1]
    assert "returniq-human-review" in call_kwargs["QueueUrl"]
    body = json.loads(call_kwargs["MessageBody"])
    assert body["return_id"] == "TEST123"
    assert body["confidence"] == 72.0


@pytest.mark.asyncio
async def test_publish_includes_message_attributes() -> None:
    client = _make_client()
    adapter = _make_adapter(client)
    request = _make_review_request()

    await adapter.publish(request)

    call_kwargs = client.send_message.call_args[1]
    attrs = call_kwargs["MessageAttributes"]
    assert attrs["ReturnId"]["StringValue"] == "TEST123"
    assert attrs["Priority"]["StringValue"] == "MEDIUM"
    assert attrs["Confidence"]["StringValue"] == "72.0"


@pytest.mark.asyncio
async def test_publish_retries_on_client_error() -> None:
    client = MagicMock()
    client.send_message.side_effect = [
        ClientError(
            {"Error": {"Code": "ServiceUnavailableException", "Message": "down"}},
            "SendMessage",
        ),
        {"MessageId": "msg-retry-ok"},
    ]
    adapter = _make_adapter(client, max_retries=1)
    request = _make_review_request()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await adapter.publish(request)

    assert result.success
    assert result.message_id == "msg-retry-ok"
    assert client.send_message.call_count == 2


@pytest.mark.asyncio
async def test_publish_raises_after_exhausting_retries() -> None:
    client = MagicMock()
    client.send_message.side_effect = ClientError(
        {"Error": {"Code": "InternalError", "Message": "permanent"}},
        "SendMessage",
    )
    adapter = _make_adapter(client, max_retries=1)
    request = _make_review_request()

    with patch("asyncio.sleep", new_callable=AsyncMock), \
         pytest.raises(InfrastructureError, match="Failed to publish"):
        await adapter.publish(request)

    assert client.send_message.call_count == 2


@pytest.mark.asyncio
async def test_publish_no_retry_when_max_retries_zero() -> None:
    client = MagicMock()
    client.send_message.side_effect = ClientError(
        {"Error": {"Code": "InternalError", "Message": "permanent"}},
        "SendMessage",
    )
    adapter = _make_adapter(client, max_retries=0)
    request = _make_review_request()

    with pytest.raises(InfrastructureError):
        await adapter.publish(request)

    assert client.send_message.call_count == 1
