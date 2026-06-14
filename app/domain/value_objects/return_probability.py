# app/domain/value_objects/return_probability.py
from __future__ import annotations

from app.domain.exceptions import DomainValidationError


class ReturnProbability:
    __slots__ = ("_value",)

    def __init__(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise DomainValidationError(f"ReturnProbability must be 0.0-1.0, got {value}")
        self._value = value

    @property
    def value(self) -> float:
        return self._value

    @property
    def risk_level(self) -> str:
        if self._value < 0.2:
            return "LOW"
        if self._value < 0.5:
            return "MEDIUM"
        return "HIGH"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReturnProbability):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"ReturnProbability({self._value})"
