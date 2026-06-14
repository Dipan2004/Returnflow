# app/domain/services/disposition_engine.py
from __future__ import annotations

from app.domain.entities.disposition_decision import DispositionDecision
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId

_P2P_RECOVERY_PCT: float = 65.0
_RESELL_RECOVERY_PCT: float = 75.0
_REFURBISH_RECOVERY_PCT: float = 55.0
_DONATE_RECOVERY_PCT: float = 0.0
_SCRAP_RECOVERY_PCT: float = 0.0
_LIQUIDATION_PCT: float = 5.0


class DispositionEngine:
    def __init__(self, p2p_max_radius_km: float = 5.0) -> None:
        if p2p_max_radius_km <= 0:
            from app.domain.exceptions import DomainValidationError

            raise DomainValidationError("p2p_max_radius_km must be positive")
        self._p2p_max_radius_km = p2p_max_radius_km

    def calculate(
        self,
        return_id: ReturnId,
        grade: Grade,
        mrp: Money,
        *,
        has_p2p_demand: bool,
        distance_km: float | None,
        matched_buyer_id: str | None,
    ) -> DispositionDecision:
        return DispositionDecision.decide(
            return_id=return_id,
            grade=grade,
            mrp=mrp,
            fraud_flagged=False,
            has_p2p_match=has_p2p_demand,
            distance_km=distance_km,
            matched_buyer_id=matched_buyer_id,
            p2p_max_radius_km=self._p2p_max_radius_km,
        )

    def calculate_with_fraud_override(
        self,
        return_id: ReturnId,
        grade: Grade,
        mrp: Money,
    ) -> DispositionDecision:
        return DispositionDecision.decide(
            return_id=return_id,
            grade=grade,
            mrp=mrp,
            fraud_flagged=True,
            has_p2p_match=False,
            distance_km=None,
            matched_buyer_id=None,
            p2p_max_radius_km=self._p2p_max_radius_km,
        )

    @staticmethod
    def recovery_percentage_for_grade(grade: Grade, has_p2p_demand: bool = False) -> float:
        if grade == Grade.A:
            return _P2P_RECOVERY_PCT if has_p2p_demand else _RESELL_RECOVERY_PCT
        if grade == Grade.B:
            return _REFURBISH_RECOVERY_PCT
        return _DONATE_RECOVERY_PCT

    @staticmethod
    def liquidation_percentage() -> float:
        return _LIQUIDATION_PCT
