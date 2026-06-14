# tests/fakes/fake_fraud_repository.py
from __future__ import annotations

from app.application.ports.fraud_repository import FraudRepository
from app.domain.entities.fraud_assessment import FraudAssessment
from app.domain.value_objects.return_id import ReturnId


class FakeFraudRepository(FraudRepository):
    def __init__(self) -> None:
        self._store: dict[str, FraudAssessment] = {}

    async def save(self, assessment: FraudAssessment) -> None:
        self._store[assessment.return_id.value] = assessment

    async def get_by_return_id(self, return_id: ReturnId) -> FraudAssessment | None:
        return self._store.get(return_id.value)

    def count(self) -> int:
        return len(self._store)
