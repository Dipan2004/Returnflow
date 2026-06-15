# app/infrastructure/persistence/in_memory_disposition_repository.py
from __future__ import annotations

from app.application.ports.disposition_repository import DispositionRepository
from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryDispositionRepository(DispositionRepository):
    def __init__(self) -> None:
        STORE.setdefault("dispositions", {})

    async def save(self, decision: DispositionDecision) -> None:
        STORE["dispositions"][decision.return_id.value] = decision

    async def get_by_return_id(self, return_id: ReturnId) -> DispositionDecision | None:
        return STORE["dispositions"].get(return_id.value)
