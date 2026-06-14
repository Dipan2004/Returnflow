# app/application/ports/disposition_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.value_objects.return_id import ReturnId


class DispositionRepository(ABC):
    """Port for persisting and retrieving DispositionDecision aggregates."""

    @abstractmethod
    async def save(self, decision: DispositionDecision) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> DispositionDecision | None: ...