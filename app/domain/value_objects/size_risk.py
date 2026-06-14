# app/domain/value_objects/size_risk.py
from __future__ import annotations

from enum import StrEnum


class SizeRisk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @classmethod
    def from_mismatch_rate(cls, rate: float) -> SizeRisk:
        if rate >= 0.5:
            return cls.HIGH
        if rate >= 0.25:
            return cls.MEDIUM
        return cls.LOW
