# tests/unit/infrastructure/test_bedrock_description_adapter.py
from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.ports.description_generation_port import DescriptionRequest
from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade
from app.infrastructure.adapters.bedrock.bedrock_description_adapter import (
    _NO_DAMAGE_DESCRIPTION,
    BedrockDescriptionAdapter,
)


def _make_client(text: str) -> MagicMock:
    client = MagicMock()
    body_stream = BytesIO(
        json.dumps({"content": [{"type": "text", "text": text}]}).encode()
    )
    client.invoke_model.return_value = {"body": body_stream}
    return client


def _make_adapter(client: MagicMock, max_retries: int = 0) -> BedrockDescriptionAdapter:
    return BedrockDescriptionAdapter(
        bedrock_client=client,
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        max_retries=max_retries,
    )


@pytest.mark.asyncio
async def test_no_damage_labels_returns_no_damage_description() -> None:
    client = _make_client("ignored")
    adapter = _make_adapter(client)
    request = DescriptionRequest(grade=Grade.A, damage_labels=[])
    result = await adapter.generate(request)
    assert result.description == _NO_DAMAGE_DESCRIPTION
    assert result.model_id == "rule-based"
    assert not result.used_fallback
    client.invoke_model.assert_not_called()


@pytest.mark.asyncio
async def test_successful_generation_returns_description() -> None:
    expected = "Minor scratch on the toe box area."
    client = _make_client(expected)
    adapter = _make_adapter(client)
    request = DescriptionRequest(
        grade=Grade.A,
        damage_labels=[DamageLabel(name="Scratch", confidence=82.0)],
    )
    result = await adapter.generate(request)
    assert result.description == expected
    assert result.model_id == "anthropic.claude-3-haiku-20240307-v1:0"
    assert not result.used_fallback


@pytest.mark.asyncio
async def test_fallback_used_on_client_error() -> None:
    from botocore.exceptions import ClientError
    client = MagicMock()
    client.invoke_model.side_effect = ClientError(
        {"Error": {"Code": "ThrottlingException", "Message": "Too many requests"}},
        "InvokeModel",
    )
    adapter = _make_adapter(client, max_retries=0)
    request = DescriptionRequest(
        grade=Grade.B,
        damage_labels=[DamageLabel(name="Dent", confidence=70.0)],
    )
    result = await adapter.generate(request)
    assert result.used_fallback
    assert result.model_id == "fallback"
    assert len(result.description) > 0


@pytest.mark.asyncio
async def test_retries_on_failure_then_succeeds() -> None:
    expected = "Moderate dent visible on left panel."
    body_ok = BytesIO(
        json.dumps({"content": [{"type": "text", "text": expected}]}).encode()
    )
    from botocore.exceptions import ClientError
    client = MagicMock()
    client.invoke_model.side_effect = [
        ClientError(
            {"Error": {"Code": "ServiceUnavailableException", "Message": "down"}},
            "InvokeModel",
        ),
        {"body": body_ok},
    ]
    adapter = _make_adapter(client, max_retries=1)
    request = DescriptionRequest(
        grade=Grade.B,
        damage_labels=[DamageLabel(name="Dent", confidence=70.0)],
    )
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await adapter.generate(request)
    assert result.description == expected
    assert not result.used_fallback
    assert client.invoke_model.call_count == 2


@pytest.mark.asyncio
async def test_word_count_in_response() -> None:
    text = "Minor scratch on the toe box area."
    client = _make_client(text)
    adapter = _make_adapter(client)
    request = DescriptionRequest(
        grade=Grade.A,
        damage_labels=[DamageLabel(name="Scratch", confidence=82.0)],
    )
    result = await adapter.generate(request)
    assert result.word_count == len(text.split())