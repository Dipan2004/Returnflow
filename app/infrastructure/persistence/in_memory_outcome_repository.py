# app/infrastructure/persistence/in_memory_outcome_repository.py
from __future__ import annotations

from app.application.ports.outcome_repository import OutcomeRepository
from app.domain.entities.disposition_outcome import DispositionOutcome
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryOutcomeRepository(OutcomeRepository):
    def __init__(self) -> None:
        STORE.setdefault("outcomes", {})

    async def save(self, outcome: DispositionOutcome) -> None:
        STORE["outcomes"][outcome.return_id.value] = outcome

    async def get_by_return_id(self, return_id: ReturnId) -> DispositionOutcome | None:
        return STORE["outcomes"].get(return_id.value)
