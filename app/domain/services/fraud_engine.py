# app/domain/services/fraud_engine.py
from __future__ import annotations

from app.domain.entities.fraud_assessment import (
    FraudAssessment,
    FraudOverrideReason,
    FraudSignal,
)
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route

_SIGNAL_EXCESSIVE_RETURNS = "EXCESSIVE_RETURN_FREQUENCY"
_SIGNAL_HIGH_VALUE_RETURNS = "HIGH_VALUE_RETURN_FREQUENCY"
_SIGNAL_REPEAT_SKU = "REPEAT_SKU_RETURN"
_SIGNAL_VELOCITY = "SUSPICIOUS_RETURN_VELOCITY"

_WEIGHT_EXCESSIVE_RETURNS = 30
_WEIGHT_HIGH_VALUE = 25
_WEIGHT_REPEAT_SKU = 25
_WEIGHT_VELOCITY = 20

_EXCESSIVE_RETURN_THRESHOLD = 5
_HIGH_VALUE_THRESHOLD = 3
_REPEAT_SKU_THRESHOLD = 2
_VELOCITY_THRESHOLD = 3
_VELOCITY_WINDOW_HOURS = 24


class FraudEngine:
    def __init__(
        self,
        bulk_buy_threshold: int = 10,
        window_hours: int = 72,
    ) -> None:
        self._bulk_buy_threshold = bulk_buy_threshold
        self._window_hours = window_hours

    def assess(
        self,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        *,
        total_returns_in_window: int,
        high_value_returns_in_window: int,
        same_sku_returns_in_window: int,
        returns_last_24h: int,
        original_route: Route | None = None,
    ) -> FraudAssessment:
        signals = [
            FraudSignal(
                name=_SIGNAL_EXCESSIVE_RETURNS,
                weight=_WEIGHT_EXCESSIVE_RETURNS,
                triggered=total_returns_in_window >= _EXCESSIVE_RETURN_THRESHOLD,
                detail=(
                    f"{total_returns_in_window} returns in {self._window_hours}h "
                    f"(threshold: {_EXCESSIVE_RETURN_THRESHOLD})"
                ),
            ),
            FraudSignal(
                name=_SIGNAL_HIGH_VALUE_RETURNS,
                weight=_WEIGHT_HIGH_VALUE,
                triggered=high_value_returns_in_window >= _HIGH_VALUE_THRESHOLD,
                detail=(
                    f"{high_value_returns_in_window} high-value returns in {self._window_hours}h "
                    f"(threshold: {_HIGH_VALUE_THRESHOLD})"
                ),
            ),
            FraudSignal(
                name=_SIGNAL_REPEAT_SKU,
                weight=_WEIGHT_REPEAT_SKU,
                triggered=same_sku_returns_in_window >= _REPEAT_SKU_THRESHOLD,
                detail=(
                    f"{same_sku_returns_in_window} returns of same SKU in {self._window_hours}h "
                    f"(threshold: {_REPEAT_SKU_THRESHOLD})"
                ),
            ),
            FraudSignal(
                name=_SIGNAL_VELOCITY,
                weight=_WEIGHT_VELOCITY,
                triggered=returns_last_24h >= _VELOCITY_THRESHOLD,
                detail=(
                    f"{returns_last_24h} returns in last 24h "
                    f"(threshold: {_VELOCITY_THRESHOLD})"
                ),
            ),
        ]

        override_reason: FraudOverrideReason | None = None
        assessment = FraudAssessment.create(
            return_id=return_id,
            buyer_id=buyer_id,
            sku_id=sku_id,
            signals=signals,
        )

        if assessment.requires_route_override and original_route is not None:
            override_reason = FraudOverrideReason(
                original_route=original_route.value,
                overridden_route=Route.RESELL.value,
                risk_level=assessment.risk_level.value,
                risk_score=assessment.risk_score,
                reason=(
                    f"Fraud risk {assessment.risk_level.value} (score: {assessment.risk_score}) "
                    f"- route overridden from {original_route.value} to RESELL"
                ),
            )
            assessment = FraudAssessment.create(
                return_id=return_id,
                buyer_id=buyer_id,
                sku_id=sku_id,
                signals=signals,
                override_reason=override_reason,
            )

        return assessment
