# tests/fakes/fake_disposition_repository.py
from __future__ import annotations

from app.application.ports.disposition_repository import DispositionRepository
from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.value_objects.return_id import ReturnId


class FakeDispositionRepository(DispositionRepository):
    def __init__(self) -> None:
        self._store: dict[str, DispositionDecision] = {}

    async def save(self, decision: DispositionDecision) -> None:
        self._store[decision.return_id.value] = decision

    async def get_by_return_id(self, return_id: ReturnId) -> DispositionDecision | None:
        return self._store.get(return_id.value)

    # --- test helper ---

    def all(self) -> list[DispositionDecision]:
        return list(self._store.values())

    def count(self) -> int:
        return len(self._store)