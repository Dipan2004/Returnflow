# app/application/ports/outcome_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.disposition_outcome import DispositionOutcome
from app.domain.value_objects.return_id import ReturnId


class OutcomeRepository(ABC):
    @abstractmethod
    async def save(self, outcome: DispositionOutcome) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> DispositionOutcome | None: ...
