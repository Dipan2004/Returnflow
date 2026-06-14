# tests/unit/application/test_verify_qr_token_use_case.py
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.application.use_cases.verify_qr_token_use_case import VerifyQrTokenUseCase
from app.domain.entities.qr_token import QRToken
from app.domain.value_objects.return_id import ReturnId
from tests.fakes.fake_health_card_repository import FakeHealthCardRepository
from tests.fakes.fake_verification_audit_repository import FakeVerificationAuditRepository


def _make_use_case() -> tuple[
    VerifyQrTokenUseCase, FakeHealthCardRepository, FakeVerificationAuditRepository
]:
    hc_repo = FakeHealthCardRepository()
    audit_repo = FakeVerificationAuditRepository()
    uc = VerifyQrTokenUseCase(
        health_card_repository=hc_repo,
        verification_audit_repository=audit_repo,
    )
    return uc, hc_repo, audit_repo


@pytest.mark.asyncio
async def test_valid_first_scan() -> None:
    uc, hc_repo, audit_repo = _make_use_case()
    rid = ReturnId.generate()
    token = QRToken.generate(rid, ttl_hours=48)
    await hc_repo.save_qr_token(token)

    result = await uc.execute(token.token, "agent_1")

    assert result.valid
    assert result.status == "VALID"
    assert result.alert == "NONE"
    assert result.return_id == rid.value
    assert audit_repo.count() == 1


@pytest.mark.asyncio
async def test_second_scan_triggers_tampering() -> None:
    uc, hc_repo, audit_repo = _make_use_case()
    rid = ReturnId.generate()
    token = QRToken.generate(rid, ttl_hours=48)
    await hc_repo.save_qr_token(token)

    await uc.execute(token.token, "agent_1")
    result = await uc.execute(token.token, "agent_2")

    assert not result.valid
    assert result.status == "ALREADY_SCANNED"
    assert result.alert == "POSSIBLE_TAMPERING"
    assert audit_repo.count() == 2


@pytest.mark.asyncio
async def test_expired_token() -> None:
    uc, hc_repo, audit_repo = _make_use_case()
    rid = ReturnId.generate()
    token = QRToken(
        token="x" * 43,
        return_id=rid,
        created_at=datetime.now(UTC) - timedelta(hours=100),
        ttl_hours=48,
    )
    await hc_repo.save_qr_token(token)

    result = await uc.execute(token.token, "agent_1")

    assert not result.valid
    assert result.status == "EXPIRED"
    assert result.alert == "NONE"


@pytest.mark.asyncio
async def test_unknown_token() -> None:
    uc, _, audit_repo = _make_use_case()

    result = await uc.execute("nonexistent_token_12345678901234567", "agent_1")

    assert not result.valid
    assert result.status == "NOT_FOUND"
    assert result.return_id is None
    assert audit_repo.count() == 1


@pytest.mark.asyncio
async def test_audit_trail_records_all_attempts() -> None:
    uc, hc_repo, audit_repo = _make_use_case()
    rid = ReturnId.generate()
    token = QRToken.generate(rid, ttl_hours=48)
    await hc_repo.save_qr_token(token)

    await uc.execute(token.token, "agent_1")
    await uc.execute(token.token, "agent_2")
    await uc.execute(token.token, "agent_3")

    assert audit_repo.count() == 3


@pytest.mark.asyncio
async def test_valid_scan_returns_agent_id() -> None:
    uc, hc_repo, _ = _make_use_case()
    rid = ReturnId.generate()
    token = QRToken.generate(rid, ttl_hours=48)
    await hc_repo.save_qr_token(token)

    result = await uc.execute(token.token, "delivery_agent_42")

    assert result.scanned_by == "delivery_agent_42"
