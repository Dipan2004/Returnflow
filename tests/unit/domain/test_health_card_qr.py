# tests/unit/domain/test_health_card_qr.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.entities.health_card import HealthCard, HealthCardStatus
from app.domain.entities.qr_token import QRToken
from app.domain.exceptions import (
    DomainValidationError,
    InvalidStateTransitionError,
    QRTokenAlreadyScannedError,
)
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route


def _make_health_card(rid: ReturnId | None = None) -> HealthCard:
    r = rid or ReturnId.generate()
    return HealthCard(
        return_id=r,
        sku_id="B08N5WRWNW",
        grade=Grade.A,
        confidence=ConfidenceScore.of(92.0),
        damage_description="Minor scratch on surface.",
        route=Route.P2P,
        mrp=Money.of(Decimal("850.00")),
        recovery_value=Money.of(Decimal("552.50")),
        value_delta=Money.of(Decimal("510.00")),
        image_keys=[ImageKey.pending(r.value, 1)],
        qr_token="a" * 43,
        qr_url="https://returniq.example.com/verify/token123",
        created_at=datetime.now(UTC),
        ttl_hours=48,
    )


class TestHealthCard:
    def test_creation_valid(self) -> None:
        hc = _make_health_card()
        assert hc.status == HealthCardStatus.PENDING_BUYER_ACCEPT

    def test_accept_transitions(self) -> None:
        hc = _make_health_card()
        hc.accept()
        assert hc.status == HealthCardStatus.ACCEPTED
        assert hc.accepted_at is not None

    def test_dispute_requires_reason(self) -> None:
        hc = _make_health_card()
        with pytest.raises(DomainValidationError):
            hc.dispute("")

    def test_dispute_transitions(self) -> None:
        hc = _make_health_card()
        hc.dispute("Item not matching photos")
        assert hc.status == HealthCardStatus.DISPUTED

    def test_invalid_transition_raises(self) -> None:
        hc = _make_health_card()
        hc.accept()
        hc.complete()
        with pytest.raises(InvalidStateTransitionError):
            hc.accept()

    def test_empty_sku_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            HealthCard(
                return_id=ReturnId.generate(),
                sku_id="",
                grade=Grade.A,
                confidence=ConfidenceScore.of(90.0),
                damage_description="x",
                route=Route.RESELL,
                mrp=Money.of(100),
                recovery_value=Money.of(75),
                value_delta=Money.of(70),
                image_keys=[ImageKey.pending("X", 1)],
                qr_token="a" * 43,
                qr_url="https://x.com/v",
                created_at=datetime.now(UTC),
                ttl_hours=48,
            )

    def test_no_images_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            HealthCard(
                return_id=ReturnId.generate(),
                sku_id="SKU",
                grade=Grade.A,
                confidence=ConfidenceScore.of(90.0),
                damage_description="x",
                route=Route.RESELL,
                mrp=Money.of(100),
                recovery_value=Money.of(75),
                value_delta=Money.of(70),
                image_keys=[],
                qr_token="a" * 43,
                qr_url="https://x.com/v",
                created_at=datetime.now(UTC),
                ttl_hours=48,
            )


class TestQRToken:
    def test_generate_produces_valid_token(self) -> None:
        rid = ReturnId.generate()
        token = QRToken.generate(rid, ttl_hours=48)
        assert len(token.token) >= 32
        assert not token.scanned
        assert token.is_valid_for_use()

    def test_consume_marks_scanned(self) -> None:
        rid = ReturnId.generate()
        token = QRToken.generate(rid)
        token.consume("agent_001")
        assert token.scanned
        assert token.scanned_by == "agent_001"
        assert token.scanned_at is not None

    def test_double_consume_raises(self) -> None:
        rid = ReturnId.generate()
        token = QRToken.generate(rid)
        token.consume("agent_001")
        with pytest.raises(QRTokenAlreadyScannedError):
            token.consume("agent_002")

    def test_short_token_raises(self) -> None:
        with pytest.raises(DomainValidationError):
            QRToken(
                token="short",
                return_id=ReturnId.generate(),
                created_at=datetime.now(UTC),
                ttl_hours=48,
            )

    def test_expires_at_computed(self) -> None:
        rid = ReturnId.generate()
        token = QRToken.generate(rid, ttl_hours=24)
        assert token.expires_at > token.created_at
