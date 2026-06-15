# app/infrastructure/persistence/in_memory_fraud_repository.py
from __future__ import annotations

from app.application.ports.fraud_repository import FraudRepository
from app.domain.entities.fraud_assessment import FraudAssessment
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.in_memory_store import STORE


class InMemoryFraudRepository(FraudRepository):
    def __init__(self) -> None:
        STORE.setdefault("fraud", {})

    async def save(self, assessment: FraudAssessment) -> None:
        STORE["fraud"][assessment.return_id.value] = assessment

    async def get_by_return_id(self, return_id: ReturnId) -> FraudAssessment | None:
        return STORE["fraud"].get(return_id.value)
