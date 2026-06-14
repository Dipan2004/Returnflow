# app/infrastructure/adapters/bedrock/response_parser.py
from __future__ import annotations

import json
import re
from typing import Any

from app.domain.exceptions import InfrastructureError

_MAX_WORDS = 25
_MIN_CHARS = 10
_SENTENCE_PATTERN = re.compile(r"[A-Za-z].*?[.!?]", re.DOTALL)


def parse_bedrock_response(raw_body: bytes) -> str:
    try:
        body: dict[str, Any] = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise InfrastructureError("Bedrock", f"Response body is not valid JSON: {exc}") from exc

    content = body.get("content")
    if not isinstance(content, list) or not content:
        raise InfrastructureError("Bedrock", "Response missing 'content' array")

    first_block = content[0]
    if not isinstance(first_block, dict) or first_block.get("type") != "text":
        raise InfrastructureError("Bedrock", "First content block is not a text block")

    raw_text: str = first_block.get("text", "").strip()
    if not raw_text:
        raise InfrastructureError("Bedrock", "Bedrock returned empty text content")

    return _clean_description(raw_text)


def _clean_description(text: str) -> str:
    text = text.strip().strip('"').strip("'").strip()
    if not text.endswith("."):
        text = text.rstrip(".,!?") + "."
    return text


def validate_description(description: str) -> str:
    word_count = len(description.split())
    if word_count > _MAX_WORDS:
        words = description.split()[:_MAX_WORDS]
        description = " ".join(words).rstrip(".,!?") + "."
    if len(description) < _MIN_CHARS:
        raise InfrastructureError(
            "Bedrock",
            f"Generated description too short ({len(description)} chars): {description!r}",
        )
    return description


def count_words(description: str) -> int:
    return len(description.split())