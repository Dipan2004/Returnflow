# tests/unit/infrastructure/test_verification_audit_mapper.py
from __future__ import annotations

from app.domain.entities.verification_audit import VerificationAuditEntry
from app.domain.entities.verification_result import TamperAlert, VerificationStatus
from app.infrastructure.persistence.verification_audit_mapper import from_item, to_item


def test_to_item_keys() -> None:
    e = VerificationAuditEntry.create(
        qr_token="tok1",
        return_id="RET1",
        agent_id="a1",
        status=VerificationStatus.VALID,
        alert=TamperAlert.NONE,
    )
    item = to_item(e)
    assert item["PK"] == "QR#tok1"
    assert item["SK"].startswith("AUDIT#")
    assert item["entity_type"] == "VERIFICATION_AUDIT"


def test_roundtrip() -> None:
    original = VerificationAuditEntry.create(
        qr_token="tok2",
        return_id="RET2",
        agent_id="a2",
        status=VerificationStatus.ALREADY_SCANNED,
        alert=TamperAlert.POSSIBLE_TAMPERING,
    )
    item = to_item(original)
    restored = from_item(item)
    assert restored.qr_token == original.qr_token
    assert restored.status == VerificationStatus.ALREADY_SCANNED
    assert restored.alert == TamperAlert.POSSIBLE_TAMPERING
    assert restored.agent_id == "a2"


def test_roundtrip_no_return_id() -> None:
    original = VerificationAuditEntry.create(
        qr_token="tok3",
        return_id=None,
        agent_id="a3",
        status=VerificationStatus.NOT_FOUND,
        alert=TamperAlert.NONE,
    )
    item = to_item(original)
    restored = from_item(item)
    assert restored.return_id is None
