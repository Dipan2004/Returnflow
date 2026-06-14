# app/domain/services/disposition_orchestrator.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities.buyer_match_result import BuyerMatchResult
from app.domain.entities.condition_grade import ConditionGrade
from app.domain.entities.fraud_assessment import FraudAssessment, FraudRiskLevel
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.money import Money
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route

_P2P_RECOVERY_PCT = 65.0
_RESELL_RECOVERY_PCT = 75.0
_REFURBISH_RECOVERY_PCT = 55.0
_LIQUIDATION_PCT = 5.0


@dataclass(frozen=True)
class OrchestratedDecision:
    return_id: ReturnId
    route: Route
    grade: Grade
    recovery_value: Money
    liquidation_baseline: Money
    mrp: Money
    confidence: float
    decision_reason: str
    demand_score: int
    fraud_override_applied: bool
    buyer_match_used: bool
    decided_at: datetime

    @property
    def value_delta(self) -> Money:
        return self.recovery_value.subtract(self.liquidation_baseline)

    @property
    def recovery_percentage(self) -> float:
        if self.mrp.amount == Decimal("0.00"):
            return 0.0
        return float(self.recovery_value.amount / self.mrp.amount * 100)


class DispositionOrchestrator:
    def __init__(self, p2p_max_radius_km: float = 5.0) -> None:
        self._p2p_max_radius_km = p2p_max_radius_km

    def decide(
        self,
        return_id: ReturnId,
        condition_grade: ConditionGrade,
        fraud_assessment: FraudAssessment,
        buyer_match: BuyerMatchResult | None,
        mrp: Money,
    ) -> OrchestratedDecision:
        grade = condition_grade.grade
        demand_score = buyer_match.demand_score.value if buyer_match else 0
        confidence = condition_grade.confidence.value

        if grade == Grade.SCRAP:
            return self._build(
                return_id=return_id,
                route=Route.SCRAP,
                grade=grade,
                mrp=mrp,
                recovery_pct=0.0,
                confidence=confidence,
                reason="Grade SCRAP - responsible disposal required",
                demand_score=demand_score,
                fraud_override=False,
                buyer_match_used=False,
            )

        if fraud_assessment.risk_level == FraudRiskLevel.HIGH:
            return self._build(
                return_id=return_id,
                route=Route.RESELL,
                grade=grade,
                mrp=mrp,
                recovery_pct=_RESELL_RECOVERY_PCT,
                confidence=confidence,
                reason=(
                    f"Fraud risk HIGH (score: {fraud_assessment.risk_score}) "
                    f"- forced to Amazon warehouse resale"
                ),
                demand_score=demand_score,
                fraud_override=True,
                buyer_match_used=False,
            )

        if grade == Grade.C or grade == Grade.DONATE:
            return self._build(
                return_id=return_id,
                route=Route.DONATE,
                grade=grade,
                mrp=mrp,
                recovery_pct=0.0,
                confidence=confidence,
                reason=f"Grade {grade.value} - routing to NGO donation",
                demand_score=demand_score,
                fraud_override=False,
                buyer_match_used=False,
            )

        if grade == Grade.B:
            return self._build(
                return_id=return_id,
                route=Route.REFURBISH,
                grade=grade,
                mrp=mrp,
                recovery_pct=_REFURBISH_RECOVERY_PCT,
                confidence=confidence,
                reason="Grade B - routing to Amazon Certified Refurbished",
                demand_score=demand_score,
                fraud_override=False,
                buyer_match_used=False,
            )

        if buyer_match is not None and buyer_match.p2p_recommended:
            return self._build(
                return_id=return_id,
                route=Route.P2P,
                grade=grade,
                mrp=mrp,
                recovery_pct=_P2P_RECOVERY_PCT,
                confidence=confidence,
                reason=(
                    f"Grade A with P2P buyer match "
                    f"(demand: {buyer_match.demand_level.value}, "
                    f"buyers: {buyer_match.estimated_buyers})"
                ),
                demand_score=demand_score,
                fraud_override=False,
                buyer_match_used=True,
            )

        if demand_score >= 70:
            return self._build(
                return_id=return_id,
                route=Route.RESELL,
                grade=grade,
                mrp=mrp,
                recovery_pct=_RESELL_RECOVERY_PCT,
                confidence=confidence,
                reason=f"Grade A with high demand (score: {demand_score}) - Amazon Resell",
                demand_score=demand_score,
                fraud_override=False,
                buyer_match_used=False,
            )

        return self._build(
            return_id=return_id,
            route=Route.RESELL,
            grade=grade,
            mrp=mrp,
            recovery_pct=_RESELL_RECOVERY_PCT,
            confidence=confidence,
            reason="Grade A - defaulting to Amazon Resell",
            demand_score=demand_score,
            fraud_override=False,
            buyer_match_used=buyer_match is not None,
        )

    def _build(
        self,
        return_id: ReturnId,
        route: Route,
        grade: Grade,
        mrp: Money,
        recovery_pct: float,
        confidence: float,
        reason: str,
        demand_score: int,
        fraud_override: bool,
        buyer_match_used: bool,
    ) -> OrchestratedDecision:
        recovery_value = mrp.percentage(recovery_pct)
        liquidation_baseline = mrp.percentage(_LIQUIDATION_PCT)
        return OrchestratedDecision(
            return_id=return_id,
            route=route,
            grade=grade,
            recovery_value=recovery_value,
            liquidation_baseline=liquidation_baseline,
            mrp=mrp,
            confidence=confidence,
            decision_reason=reason,
            demand_score=demand_score,
            fraud_override_applied=fraud_override,
            buyer_match_used=buyer_match_used,
            decided_at=datetime.now(UTC),
        )
