# tests/unit/domain/test_verification.py
from __future__ import annotations

from datetime import UTC, datetime

from app.domain.entities.verification_audit import VerificationAuditEntry
from app.domain.entities.verification_result import (
    TamperAlert,
    VerificationResult,
    VerificationStatus,
)


class TestVerificationResult:
    def test_valid_result(self) -> None:
        r = VerificationResult.valid("tok123", "RET1", "agent_1")
        assert r.status == VerificationStatus.VALID
        assert r.alert == TamperAlert.NONE
        assert r.return_id == "RET1"
        assert r.scanned_by == "agent_1"
        assert r.scanned_at is not None

    def test_already_scanned_result(self) -> None:
        prev = datetime.now(UTC)
        r = VerificationResult.already_scanned("tok123", "RET1", prev)
        assert r.status == VerificationStatus.ALREADY_SCANNED
        assert r.alert == TamperAlert.POSSIBLE_TAMPERING
        assert r.previous_scan_at == prev

    def test_expired_result(self) -> None:
        r = VerificationResult.expired("tok123", "RET1")
        assert r.status == VerificationStatus.EXPIRED
        assert r.alert == TamperAlert.NONE

    def test_not_found_result(self) -> None:
        r = VerificationResult.not_found("tok123")
        assert r.status == VerificationStatus.NOT_FOUND
        assert r.return_id is None

    def test_valid_has_no_previous_scan(self) -> None:
        r = VerificationResult.valid("tok", "RET", "ag")
        assert r.previous_scan_at is None


class TestVerificationAuditEntry:
    def test_create_entry(self) -> None:
        e = VerificationAuditEntry.create(
            qr_token="tok1",
            return_id="RET1",
            agent_id="agent_1",
            status=VerificationStatus.VALID,
            alert=TamperAlert.NONE,
        )
        assert e.qr_token == "tok1"
        assert e.agent_id == "agent_1"
        assert e.verified_at is not None

    def test_create_tampering_entry(self) -> None:
        e = VerificationAuditEntry.create(
            qr_token="tok2",
            return_id="RET2",
            agent_id="agent_2",
            status=VerificationStatus.ALREADY_SCANNED,
            alert=TamperAlert.POSSIBLE_TAMPERING,
        )
        assert e.alert == TamperAlert.POSSIBLE_TAMPERING

    def test_create_not_found_entry(self) -> None:
        e = VerificationAuditEntry.create(
            qr_token="unknown",
            return_id=None,
            agent_id="agent_3",
            status=VerificationStatus.NOT_FOUND,
            alert=TamperAlert.NONE,
        )
        assert e.return_id is None
