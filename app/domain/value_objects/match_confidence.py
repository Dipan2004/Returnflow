# app/domain/value_objects/match_confidence.py
from __future__ import annotations

from enum import StrEnum


class MatchConfidence(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
