# app/domain/entities/fraud_assessment.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


class FraudRiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @classmethod
    def from_score(cls, score: int) -> FraudRiskLevel:
        if score < 0 or score > 100:
            raise DomainValidationError(f"Fraud score must be 0-100, got {score}")
        if score >= 70:
            return cls.HIGH
        if score >= 40:
            return cls.MEDIUM
        return cls.LOW


@dataclass(frozen=True)
class FraudSignal:
    name: str
    weight: int
    triggered: bool
    detail: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise DomainValidationError("FraudSignal name cannot be empty")
        if self.weight < 0 or self.weight > 100:
            raise DomainValidationError(f"FraudSignal weight must be 0-100, got {self.weight}")


@dataclass(frozen=True)
class FraudOverrideReason:
    original_route: str
    overridden_route: str
    risk_level: str
    risk_score: int
    reason: str


class FraudAssessment:
    def __init__(
        self,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        risk_score: int,
        risk_level: FraudRiskLevel,
        signals: list[FraudSignal],
        override_reason: FraudOverrideReason | None,
        assessed_at: datetime,
    ) -> None:
        if not buyer_id or not buyer_id.strip():
            raise DomainValidationError("buyer_id cannot be empty")
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if risk_score < 0 or risk_score > 100:
            raise DomainValidationError(f"risk_score must be 0-100, got {risk_score}")
        self._return_id = return_id
        self._buyer_id = buyer_id.strip()
        self._sku_id = sku_id.strip()
        self._risk_score = risk_score
        self._risk_level = risk_level
        self._signals = list(signals)
        self._override_reason = override_reason
        self._assessed_at = assessed_at

    @classmethod
    def create(
        cls,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        signals: list[FraudSignal],
        override_reason: FraudOverrideReason | None = None,
    ) -> FraudAssessment:
        triggered = [s for s in signals if s.triggered]
        score = min(100, sum(s.weight for s in triggered))
        level = FraudRiskLevel.from_score(score)
        return cls(
            return_id=return_id,
            buyer_id=buyer_id,
            sku_id=sku_id,
            risk_score=score,
            risk_level=level,
            signals=signals,
            override_reason=override_reason,
            assessed_at=datetime.now(UTC),
        )

    @property
    def requires_route_override(self) -> bool:
        return self._risk_level == FraudRiskLevel.HIGH

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def buyer_id(self) -> str:
        return self._buyer_id

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def risk_score(self) -> int:
        return self._risk_score

    @property
    def risk_level(self) -> FraudRiskLevel:
        return self._risk_level

    @property
    def signals(self) -> list[FraudSignal]:
        return list(self._signals)

    @property
    def triggered_signals(self) -> list[FraudSignal]:
        return [s for s in self._signals if s.triggered]

    @property
    def override_reason(self) -> FraudOverrideReason | None:
        return self._override_reason

    @property
    def assessed_at(self) -> datetime:
        return self._assessed_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FraudAssessment):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)
