# tests/fakes/fake_outcome_repository.py
from __future__ import annotations

from app.application.ports.outcome_repository import OutcomeRepository
from app.domain.entities.disposition_outcome import DispositionOutcome
from app.domain.value_objects.return_id import ReturnId


class FakeOutcomeRepository(OutcomeRepository):
    def __init__(self) -> None:
        self._store: dict[str, DispositionOutcome] = {}

    async def save(self, outcome: DispositionOutcome) -> None:
        self._store[outcome.return_id.value] = outcome

    async def get_by_return_id(self, return_id: ReturnId) -> DispositionOutcome | None:
        return self._store.get(return_id.value)

    def count(self) -> int:
        return len(self._store)
