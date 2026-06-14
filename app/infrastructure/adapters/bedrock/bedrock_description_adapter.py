# app/infrastructure/adapters/bedrock/bedrock_description_adapter.py
from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from botocore.exceptions import ClientError

from app.application.ports.description_generation_port import (
    DescriptionGenerationPort,
    DescriptionRequest,
    DescriptionResponse,
)
from app.domain.entities.condition_grade import DamageLabel
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.grade import Grade
from app.infrastructure.adapters.bedrock.prompt_templates import (
    build_system_prompt,
    build_user_prompt,
)
from app.infrastructure.adapters.bedrock.response_parser import (
    count_words,
    parse_bedrock_response,
    validate_description,
)
from app.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

logger = get_logger(__name__)

_NO_DAMAGE_DESCRIPTION = "No visible damage detected. Product appears in excellent condition."
_FALLBACK_DESCRIPTIONS: dict[Grade, str] = {
    Grade.A: "Minor cosmetic imperfection noted. Product is fully functional.",
    Grade.B: "Moderate visible damage present. Core functionality unaffected.",
    Grade.C: "Significant damage visible on product surface.",
    Grade.DONATE: "Extensive damage. Product is not suitable for resale.",
    Grade.SCRAP: "Severe structural damage. Product is at end of life.",
}


class BedrockDescriptionAdapter(DescriptionGenerationPort):
    def __init__(
        self,
        bedrock_client: BedrockRuntimeClient,
        model_id: str,
        max_retries: int = 2,
        max_tokens: int = 80,
    ) -> None:
        self._client = bedrock_client
        self._model_id = model_id
        self._max_retries = max_retries
        self._max_tokens = max_tokens

    async def generate(self, request: DescriptionRequest) -> DescriptionResponse:
        if not request.damage_labels:
            return DescriptionResponse(
                description=_NO_DAMAGE_DESCRIPTION,
                model_id="rule-based",
                word_count=count_words(_NO_DAMAGE_DESCRIPTION),
                used_fallback=False,
            )

        for attempt in range(self._max_retries + 1):
            try:
                description = await self._invoke(request.grade, request.damage_labels)
                validated = validate_description(description)
                logger.info(
                    "Bedrock description generated",
                    grade=request.grade.value,
                    words=count_words(validated),
                    attempt=attempt,
                )
                return DescriptionResponse(
                    description=validated,
                    model_id=self._model_id,
                    word_count=count_words(validated),
                    used_fallback=False,
                )
            except InfrastructureError:
                if attempt == self._max_retries:
                    break
                await asyncio.sleep(0.5 * (attempt + 1))
            except Exception as exc:
                logger.warning(
                    "Bedrock unexpected error",
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt == self._max_retries:
                    break
                await asyncio.sleep(0.5 * (attempt + 1))

        fallback = _FALLBACK_DESCRIPTIONS.get(
            request.grade, "Product condition could not be assessed automatically."
        )
        logger.warning(
            "Using fallback description after Bedrock failures",
            grade=request.grade.value,
        )
        return DescriptionResponse(
            description=fallback,
            model_id="fallback",
            word_count=count_words(fallback),
            used_fallback=True,
        )

    async def _invoke(self, grade: Grade, damage_labels: list[DamageLabel]) -> str:
        payload: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self._max_tokens,
            "system": build_system_prompt(),
            "messages": [
                {
                    "role": "user",
                    "content": build_user_prompt(grade, damage_labels),
                }
            ],
        }
        try:
            response = await asyncio.to_thread(
                self._client.invoke_model,
                modelId=self._model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json",
            )
        except ClientError as exc:
            raise InfrastructureError("Bedrock", str(exc)) from exc

        raw_body: bytes = response["body"].read()
        return parse_bedrock_response(raw_body)