# app/domain/value_objects/demand_level.py | 22 lines
from __future__ import annotations

from enum import StrEnum


class DemandLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @classmethod
    def from_score(cls, score: int) -> DemandLevel:
        if score >= 70:
            return cls.HIGH
        if score >= 40:
            return cls.MEDIUM
        return cls.LOW