# app/domain/value_objects/keep_rate.py
from __future__ import annotations

from app.domain.exceptions import DomainValidationError


class KeepRate:
    __slots__ = ("_value",)

    def __init__(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise DomainValidationError(f"KeepRate must be 0.0-1.0, got {value}")
        self._value = value

    @property
    def value(self) -> float:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KeepRate):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"KeepRate({self._value})"
