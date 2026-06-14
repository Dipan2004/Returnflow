# app/application/use_cases/fraud_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FraudSignalDTO:
    name: str
    weight: int
    triggered: bool
    detail: str


@dataclass(frozen=True)
class FraudOverrideDTO:
    original_route: str
    overridden_route: str
    risk_level: str
    risk_score: int
    reason: str


@dataclass(frozen=True)
class FraudAssessmentRequest:
    return_id: str
    buyer_id: str
    sku_id: str
    original_route: str | None = None


@dataclass(frozen=True)
class FraudAssessmentResponse:
    return_id: str
    buyer_id: str
    sku_id: str
    risk_score: int
    risk_level: str
    signals: list[FraudSignalDTO]
    override: FraudOverrideDTO | None
    assessed_at: datetime
