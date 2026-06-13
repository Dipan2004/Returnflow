from __future__ import annotations

from app.domain.exceptions import DomainValidationError


class ConfidenceScore:
    __slots__ = ("_value",)

    def __init__(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise DomainValidationError(f"ConfidenceScore must be numeric, got {type(value)}")
        if not 0.0 <= value <= 100.0:
            raise DomainValidationError(
                f"ConfidenceScore must be between 0.0 and 100.0, got {value}"
            )
        self._value = round(float(value), 1)

    @classmethod
    def of(cls, value: float) -> ConfidenceScore:
        return cls(value)

    @property
    def value(self) -> float:
        return self._value

    def meets_threshold(self, threshold: float) -> bool:
        return self._value >= threshold

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self._value == other._value

    def __lt__(self, other: ConfidenceScore) -> bool:
        return self._value < other._value

    def __le__(self, other: ConfidenceScore) -> bool:
        return self._value <= other._value

    def __gt__(self, other: ConfidenceScore) -> bool:
        return self._value > other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return f"{self._value}%"

    def __repr__(self) -> str:
        return f"ConfidenceScore({self._value})"