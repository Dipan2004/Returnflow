# app/application/use_cases/verify_qr_token_use_case.py
from __future__ import annotations

from app.application.ports.health_card_repository import HealthCardRepository
from app.application.ports.verification_audit_repository import VerificationAuditRepository
from app.application.use_cases.verification_dto import VerificationResultDTO
from app.domain.entities.verification_audit import VerificationAuditEntry
from app.domain.entities.verification_result import (
    TamperAlert,
    VerificationResult,
    VerificationStatus,
)
from app.domain.exceptions import QRTokenAlreadyScannedError
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class VerifyQrTokenUseCase:
    def __init__(
        self,
        health_card_repository: HealthCardRepository,
        verification_audit_repository: VerificationAuditRepository,
    ) -> None:
        self._health_cards = health_card_repository
        self._audit = verification_audit_repository

    async def execute(self, qr_token: str, agent_id: str) -> VerificationResultDTO:
        token_entity = await self._health_cards.get_qr_token(qr_token)

        if token_entity is None:
            result = VerificationResult.not_found(qr_token)
            audit = VerificationAuditEntry.create(
                qr_token=qr_token,
                return_id=None,
                agent_id=agent_id,
                status=VerificationStatus.NOT_FOUND,
                alert=TamperAlert.NONE,
            )
            await self._audit.save(audit)
            return self._to_dto(result)

        return_id = token_entity.return_id.value

        if token_entity.is_expired():
            result = VerificationResult.expired(qr_token, return_id)
            audit = VerificationAuditEntry.create(
                qr_token=qr_token,
                return_id=return_id,
                agent_id=agent_id,
                status=VerificationStatus.EXPIRED,
                alert=TamperAlert.NONE,
            )
            await self._audit.save(audit)
            return self._to_dto(result)

        if token_entity.scanned:
            result = VerificationResult.already_scanned(
                qr_token, return_id, token_entity.scanned_at
            )
            audit = VerificationAuditEntry.create(
                qr_token=qr_token,
                return_id=return_id,
                agent_id=agent_id,
                status=VerificationStatus.ALREADY_SCANNED,
                alert=TamperAlert.POSSIBLE_TAMPERING,
            )
            await self._audit.save(audit)
            logger.warning(
                "Tamper alert: QR already scanned",
                qr_token=qr_token[:8],
                return_id=return_id,
            )
            return self._to_dto(result)

        try:
            await self._health_cards.consume_qr_token(qr_token, agent_id)
        except QRTokenAlreadyScannedError:
            result = VerificationResult.already_scanned(
                qr_token, return_id, token_entity.scanned_at
            )
            audit = VerificationAuditEntry.create(
                qr_token=qr_token,
                return_id=return_id,
                agent_id=agent_id,
                status=VerificationStatus.ALREADY_SCANNED,
                alert=TamperAlert.POSSIBLE_TAMPERING,
            )
            await self._audit.save(audit)
            return self._to_dto(result)

        result = VerificationResult.valid(qr_token, return_id, agent_id)
        audit = VerificationAuditEntry.create(
            qr_token=qr_token,
            return_id=return_id,
            agent_id=agent_id,
            status=VerificationStatus.VALID,
            alert=TamperAlert.NONE,
        )
        await self._audit.save(audit)

        logger.info(
            "QR verification successful",
            qr_token=qr_token[:8],
            return_id=return_id,
            agent_id=agent_id,
        )
        return self._to_dto(result)

    def _to_dto(self, result: VerificationResult) -> VerificationResultDTO:
        return VerificationResultDTO(
            qr_token=result.qr_token,
            valid=result.status == VerificationStatus.VALID,
            status=result.status.value,
            alert=result.alert.value,
            return_id=result.return_id,
            scanned_by=result.scanned_by,
            scanned_at=result.scanned_at,
            previous_scan_at=result.previous_scan_at,
        )
