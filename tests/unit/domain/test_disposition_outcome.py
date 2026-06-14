# tests/unit/domain/test_disposition_outcome.py
from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.entities.disposition_outcome import DispositionOutcome, OutcomeStatus
from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


def _make_outcome() -> DispositionOutcome:
    return DispositionOutcome.create_pending(
        return_id=ReturnId.generate(),
        buyer_id="buyer_1",
        route="P2P",
        recovery_value=Decimal("6500.00"),
    )


class TestDispositionOutcome:
    def test_create_pending(self) -> None:
        o = _make_outcome()
        assert o.status == OutcomeStatus.PENDING
        assert o.resolved_at is None

    def test_accept(self) -> None:
        o = _make_outcome()
        o.accept()
        assert o.status == OutcomeStatus.ACCEPTED
        assert o.resolved_at is not None

    def test_reject(self) -> None:
        o = _make_outcome()
        o.reject("Item not as described")
        assert o.status == OutcomeStatus.REJECTED
        assert "not as described" in o.outcome_reason

    def test_dispute_from_pending(self) -> None:
        o = _make_outcome()
        o.dispute("Condition mismatch")
        assert o.status == OutcomeStatus.DISPUTED

    def test_dispute_from_accepted(self) -> None:
        o = _make_outcome()
        o.accept()
        o.dispute("Changed mind")
        assert o.status == OutcomeStatus.DISPUTED

    def test_expire(self) -> None:
        o = _make_outcome()
        o.expire()
        assert o.status == OutcomeStatus.EXPIRED

    def test_cannot_accept_twice(self) -> None:
        o = _make_outcome()
        o.accept()
        with pytest.raises(DomainValidationError):
            o.accept()

    def test_cannot_reject_after_accept(self) -> None:
        o = _make_outcome()
        o.accept()
        with pytest.raises(DomainValidationError):
            o.reject("too late")

    def test_empty_buyer_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            DispositionOutcome.create_pending(
                return_id=ReturnId.generate(),
                buyer_id="",
                route="P2P",
                recovery_value=Decimal("100"),
            )

    def test_negative_recovery_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            DispositionOutcome.create_pending(
                return_id=ReturnId.generate(),
                buyer_id="buyer",
                route="P2P",
                recovery_value=Decimal("-1"),
            )

    def test_empty_reject_reason_raises(self) -> None:
        o = _make_outcome()
        with pytest.raises(DomainValidationError):
            o.reject("")

    def test_fraud_flag_stored(self) -> None:
        o = DispositionOutcome.create_pending(
            return_id=ReturnId.generate(),
            buyer_id="buyer",
            route="RESELL",
            recovery_value=Decimal("7500"),
            fraud_flag=True,
        )
        assert o.fraud_flag is True
