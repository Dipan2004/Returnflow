# app/application/use_cases/get_disposition_use_case.py
from __future__ import annotations

from app.application.ports.disposition_repository import DispositionRepository
from app.application.use_cases.disposition_dto import (
    DispositionResponse,
    RecoveryBreakdown,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetDispositionUseCase:
    def __init__(self, disposition_repository: DispositionRepository) -> None:
        self._dispositions = disposition_repository

    async def execute(self, return_id_str: str) -> DispositionResponse:
        return_id = ReturnId(return_id_str)
        decision = await self._dispositions.get_by_return_id(return_id)
        if decision is None:
            raise EntityNotFoundError("DispositionDecision", return_id_str)

        mrp_amount = decision.mrp.amount
        recovery_pct = (
            float(decision.recovery_value.amount / mrp_amount * 100)
            if mrp_amount
            else 0.0
        )

        return DispositionResponse(
            return_id=return_id_str,
            route=decision.route.value,
            route_label=decision.route.display_label,
            grade=decision.grade.value,
            route_reason=decision.route_reason,
            recovery=RecoveryBreakdown(
                mrp=decision.mrp.amount,
                recovery_value=decision.recovery_value.amount,
                liquidation_baseline=decision.liquidation_baseline.amount,
                value_delta=decision.value_delta.amount,
                recovery_percentage=recovery_pct,
            ),
            fraud_flagged=decision.fraud_flagged,
            matched_buyer_id=decision.matched_buyer_id,
            distance_km=decision.distance_km,
            decided_at=decision.decided_at,
        )