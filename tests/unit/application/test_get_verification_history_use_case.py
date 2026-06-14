# tests/unit/application/test_get_verification_history_use_case.py
from __future__ import annotations

import pytest

from app.application.use_cases.get_verification_history_use_case import (
    GetVerificationHistoryUseCase,
)
from app.domain.entities.verification_audit import VerificationAuditEntry
from app.domain.entities.verification_result import TamperAlert, VerificationStatus
from tests.fakes.fake_verification_audit_repository import FakeVerificationAuditRepository


@pytest.mark.asyncio
async def test_empty_history() -> None:
    repo = FakeVerificationAuditRepository()
    uc = GetVerificationHistoryUseCase(verification_audit_repository=repo)
    result = await uc.execute("tok_unknown")
    assert result.total_scans == 0
    assert result.entries == []


@pytest.mark.asyncio
async def test_history_with_entries() -> None:
    repo = FakeVerificationAuditRepository()
    entry1 = VerificationAuditEntry.create(
        qr_token="tok1",
        return_id="RET1",
        agent_id="a1",
        status=VerificationStatus.VALID,
        alert=TamperAlert.NONE,
    )
    entry2 = VerificationAuditEntry.create(
        qr_token="tok1",
        return_id="RET1",
        agent_id="a2",
        status=VerificationStatus.ALREADY_SCANNED,
        alert=TamperAlert.POSSIBLE_TAMPERING,
    )
    await repo.save(entry1)
    await repo.save(entry2)

    uc = GetVerificationHistoryUseCase(verification_audit_repository=repo)
    result = await uc.execute("tok1")

    assert result.total_scans == 2
    assert result.entries[0].agent_id == "a1"
    assert result.entries[1].alert == "POSSIBLE_TAMPERING"


@pytest.mark.asyncio
async def test_history_filters_by_token() -> None:
    repo = FakeVerificationAuditRepository()
    await repo.save(
        VerificationAuditEntry.create(
            qr_token="tok_a",
            return_id="R1",
            agent_id="a1",
            status=VerificationStatus.VALID,
            alert=TamperAlert.NONE,
        )
    )
    await repo.save(
        VerificationAuditEntry.create(
            qr_token="tok_b",
            return_id="R2",
            agent_id="a2",
            status=VerificationStatus.VALID,
            alert=TamperAlert.NONE,
        )
    )

    uc = GetVerificationHistoryUseCase(verification_audit_repository=repo)
    result = await uc.execute("tok_a")
    assert result.total_scans == 1
