# tests/fakes/fake_description_generation_port.py
from __future__ import annotations

from app.application.ports.description_generation_port import (
    DescriptionGenerationPort,
    DescriptionRequest,
    DescriptionResponse,
)


class FakeDescriptionGenerationPort(DescriptionGenerationPort):
    def __init__(
        self,
        description: str = "Minor scratch visible on top surface.",
        used_fallback: bool = False,
        model_id: str = "fake",
    ) -> None:
        self._description = description
        self._used_fallback = used_fallback
        self._model_id = model_id
        self.calls: list[DescriptionRequest] = []

    async def generate(self, request: DescriptionRequest) -> DescriptionResponse:
        self.calls.append(request)
        return DescriptionResponse(
            description=self._description,
            model_id=self._model_id,
            word_count=len(self._description.split()),
            used_fallback=self._used_fallback,
        )