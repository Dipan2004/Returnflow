# tests/unit/infrastructure/test_health_card_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.health_card import HealthCard, HealthCardStatus
from app.domain.entities.qr_token import QRToken
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route
from app.infrastructure.persistence.health_card_mapper import (
    from_item as hc_from_item,
)
from app.infrastructure.persistence.health_card_mapper import (
    to_item as hc_to_item,
)
from app.infrastructure.persistence.qr_token_mapper import (
    from_item as qr_from_item,
)
from app.infrastructure.persistence.qr_token_mapper import (
    to_item as qr_to_item,
)


def _make_hc() -> HealthCard:
    rid = ReturnId.generate()
    return HealthCard(
        return_id=rid,
        sku_id="SKU1",
        grade=Grade.A,
        confidence=ConfidenceScore.of(91.0),
        damage_description="Test.",
        route=Route.RESELL,
        mrp=Money.of(Decimal("1000.00")),
        recovery_value=Money.of(Decimal("750.00")),
        value_delta=Money.of(Decimal("700.00")),
        image_keys=[ImageKey.pending(rid.value, 1)],
        qr_token="x" * 43,
        qr_url="https://x.com/verify/tok",
        created_at=datetime.now(UTC),
        ttl_hours=48,
    )


def test_health_card_roundtrip() -> None:
    original = _make_hc()
    item = hc_to_item(original)
    restored = hc_from_item(item)
    assert restored.return_id == original.return_id
    assert restored.grade == original.grade
    assert restored.route == original.route
    assert restored.recovery_value == original.recovery_value
    assert restored.status == HealthCardStatus.PENDING_BUYER_ACCEPT


def test_health_card_pk_sk() -> None:
    hc = _make_hc()
    item = hc_to_item(hc)
    assert item["PK"] == f"RETURN#{hc.return_id.value}"
    assert item["SK"] == "HEALTH_CARD"


def test_qr_token_roundtrip() -> None:
    rid = ReturnId.generate()
    token = QRToken.generate(rid, ttl_hours=24)
    item = qr_to_item(token)
    restored = qr_from_item(item)
    assert restored.token == token.token
    assert restored.return_id == token.return_id
    assert restored.ttl_hours == 24
    assert not restored.scanned


def test_qr_token_pk_sk() -> None:
    rid = ReturnId.generate()
    token = QRToken.generate(rid)
    item = qr_to_item(token)
    assert item["PK"] == f"QR#{token.token}"
    assert item["SK"] == "META"


def test_qr_token_scanned_roundtrip() -> None:
    rid = ReturnId.generate()
    token = QRToken.generate(rid)
    token.consume("agent_1")
    item = qr_to_item(token)
    restored = qr_from_item(item)
    assert restored.scanned
    assert restored.scanned_by == "agent_1"
