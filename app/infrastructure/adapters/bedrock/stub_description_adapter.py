# app/infrastructure/adapters/bedrock/stub_description_adapter.py
from __future__ import annotations

from app.application.ports.description_generation_port import (
    DescriptionGenerationPort,
    DescriptionRequest,
    DescriptionResponse,
)


class StubDescriptionAdapter(DescriptionGenerationPort):
    async def generate(self, request: DescriptionRequest) -> DescriptionResponse:
        return DescriptionResponse(
            description="Item shows minor cosmetic wear consistent with grade.",
            model_id="demo-stub",
            word_count=9,
            used_fallback=False,
        )
