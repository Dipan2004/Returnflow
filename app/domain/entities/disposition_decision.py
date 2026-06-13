from __future__ import annotations

from datetime import datetime, timezone

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route

_LIQUIDATION_PERCENTAGE = 5.0

_RECOVERY_PERCENTAGES: dict[Route, float] = {
    Route.P2P: 65.0,
    Route.RESELL: 75.0,
    Route.REFURBISH: 55.0,
    Route.DONATE: 0.0,
    Route.SCRAP: 0.0,
    Route.HUMAN_REVIEW: 0.0,
}

_GRADE_TO_DEFAULT_ROUTE: dict[Grade, Route] = {
    Grade.A: Route.RESELL,
    Grade.B: Route.REFURBISH,
    Grade.C: Route.DONATE,
    Grade.DONATE: Route.DONATE,
    Grade.SCRAP: Route.SCRAP,
}


class DispositionDecision:
    def __init__(
        self,
        return_id: ReturnId,
        route: Route,
        grade: Grade,
        mrp: Money,
        recovery_value: Money,
        liquidation_baseline: Money,
        route_reason: str,
        fraud_flagged: bool,
        decided_at: datetime,
        matched_buyer_id: str | None = None,
        distance_km: float | None = None,
    ) -> None:
        if fraud_flagged and route == Route.P2P:
            raise DomainValidationError(
                "P2P route cannot be assigned when fraud is flagged"
            )
        if distance_km is not None and distance_km < 0:
            raise DomainValidationError(
                f"distance_km cannot be negative, got {distance_km}"
            )
        if route == Route.P2P and matched_buyer_id is None:
            raise DomainValidationError(
                "P2P route requires a matched_buyer_id"
            )

        self._return_id = return_id
        self._route = route
        self._grade = grade
        self._mrp = mrp
        self._recovery_value = recovery_value
        self._liquidation_baseline = liquidation_baseline
        self._route_reason = route_reason.strip()
        self._fraud_flagged = fraud_flagged
        self._decided_at = decided_at
        self._matched_buyer_id = matched_buyer_id
        self._distance_km = distance_km

    @classmethod
    def decide(
        cls,
        return_id: ReturnId,
        grade: Grade,
        mrp: Money,
        fraud_flagged: bool,
        has_p2p_match: bool,
        distance_km: float | None,
        matched_buyer_id: str | None,
        p2p_max_radius_km: float,
    ) -> DispositionDecision:
        liquidation = mrp.percentage(_LIQUIDATION_PERCENTAGE)

        p2p_eligible = (
            grade.is_p2p_eligible
            and has_p2p_match
            and not fraud_flagged
            and distance_km is not None
            and distance_km <= p2p_max_radius_km
        )

        if p2p_eligible:
            route = Route.P2P
            route_reason = (
                f"Grade A item with buyer {distance_km:.1f}km away — P2P match selected"
            )
        elif fraud_flagged:
            route = Route.RESELL
            route_reason = "Fraud flag active — overriding to Amazon warehouse resale"
        else:
            route = _GRADE_TO_DEFAULT_ROUTE[grade]
            route_reason = f"Grade {grade.value} — defaulting to {route.display_label}"

        recovery_pct = _RECOVERY_PERCENTAGES[route]
        recovery_value = mrp.percentage(recovery_pct)

        return cls(
            return_id=return_id,
            route=route,
            grade=grade,
            mrp=mrp,
            recovery_value=recovery_value,
            liquidation_baseline=liquidation,
            route_reason=route_reason,
            fraud_flagged=fraud_flagged,
            decided_at=datetime.now(timezone.utc),
            matched_buyer_id=matched_buyer_id if p2p_eligible else None,
            distance_km=distance_km if p2p_eligible else None,
        )

    @property
    def value_delta(self) -> Money:
        return self._recovery_value.subtract(self._liquidation_baseline)

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def route(self) -> Route:
        return self._route

    @property
    def grade(self) -> Grade:
        return self._grade

    @property
    def mrp(self) -> Money:
        return self._mrp

    @property
    def recovery_value(self) -> Money:
        return self._recovery_value

    @property
    def liquidation_baseline(self) -> Money:
        return self._liquidation_baseline

    @property
    def route_reason(self) -> str:
        return self._route_reason

    @property
    def fraud_flagged(self) -> bool:
        return self._fraud_flagged

    @property
    def decided_at(self) -> datetime:
        return self._decided_at

    @property
    def matched_buyer_id(self) -> str | None:
        return self._matched_buyer_id

    @property
    def distance_km(self) -> float | None:
        return self._distance_km

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DispositionDecision):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)

    def __repr__(self) -> str:
        return (
            f"DispositionDecision(return_id={self._return_id}, route={self._route.value}, "
            f"recovery={self._recovery_value})"
        )