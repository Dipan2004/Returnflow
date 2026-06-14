# tests/unit/infrastructure/test_response_parser.py
from __future__ import annotations

import json

import pytest

from app.domain.exceptions import InfrastructureError
from app.infrastructure.adapters.bedrock.response_parser import (
    count_words,
    parse_bedrock_response,
    validate_description,
)


def _make_body(text: str) -> bytes:
    return json.dumps({"content": [{"type": "text", "text": text}]}).encode()


def test_parse_valid_response() -> None:
    body = _make_body("Minor scratch on the toe box area.")
    result = parse_bedrock_response(body)
    assert result == "Minor scratch on the toe box area."


def test_parse_adds_period_if_missing() -> None:
    body = _make_body("Minor scratch on the toe box area")
    result = parse_bedrock_response(body)
    assert result.endswith(".")


def test_parse_strips_quotes() -> None:
    body = _make_body('"Minor scratch on the toe box area."')
    result = parse_bedrock_response(body)
    assert not result.startswith('"')


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(InfrastructureError):
        parse_bedrock_response(b"not json")


def test_parse_empty_content_raises() -> None:
    body = json.dumps({"content": []}).encode()
    with pytest.raises(InfrastructureError):
        parse_bedrock_response(body)


def test_parse_missing_content_raises() -> None:
    body = json.dumps({"other": "field"}).encode()
    with pytest.raises(InfrastructureError):
        parse_bedrock_response(body)


def test_validate_truncates_over_25_words() -> None:
    long_text = " ".join(["word"] * 30) + "."
    result = validate_description(long_text)
    assert count_words(result) <= 25


def test_validate_raises_if_too_short() -> None:
    with pytest.raises(InfrastructureError):
        validate_description("Hi.")


def test_count_words() -> None:
    assert count_words("Minor scratch on the toe.") == 5