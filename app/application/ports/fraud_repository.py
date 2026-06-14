# app/application/ports/fraud_repository.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.fraud_assessment import FraudAssessment
from app.domain.value_objects.return_id import ReturnId


class FraudRepository(ABC):
    @abstractmethod
    async def save(self, assessment: FraudAssessment) -> None: ...

    @abstractmethod
    async def get_by_return_id(self, return_id: ReturnId) -> FraudAssessment | None: ...
