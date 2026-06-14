# tests/unit/infrastructure/test_outcome_mapper.py
from __future__ import annotations

from decimal import Decimal

from app.domain.entities.disposition_outcome import DispositionOutcome, OutcomeStatus
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.persistence.outcome_mapper import from_item, to_item


def test_roundtrip_pending() -> None:
    original = DispositionOutcome.create_pending(
        return_id=ReturnId("TEST1"),
        buyer_id="buyer_1",
        route="P2P",
        recovery_value=Decimal("6500.00"),
    )
    item = to_item(original)
    restored = from_item(item)
    assert restored.return_id == original.return_id
    assert restored.status == OutcomeStatus.PENDING
    assert restored.recovery_value == Decimal("6500.00")


def test_roundtrip_accepted() -> None:
    original = DispositionOutcome.create_pending(
        return_id=ReturnId("TEST2"),
        buyer_id="buyer_1",
        route="RESELL",
        recovery_value=Decimal("7500.00"),
    )
    original.accept()
    item = to_item(original)
    restored = from_item(item)
    assert restored.status == OutcomeStatus.ACCEPTED
    assert restored.resolved_at is not None


def test_pk_sk() -> None:
    o = DispositionOutcome.create_pending(
        return_id=ReturnId("TEST3"),
        buyer_id="b",
        route="P2P",
        recovery_value=Decimal("100"),
    )
    item = to_item(o)
    assert item["PK"] == "RETURN#TEST3"
    assert item["SK"] == "OUTCOME"
