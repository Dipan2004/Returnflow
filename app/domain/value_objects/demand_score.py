# app/domain/value_objects/demand_score.py | 32 lines
from __future__ import annotations

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.demand_level import DemandLevel


class DemandScore:
    __slots__ = ("_value",)

    def __init__(self, value: int) -> None:
        if not (0 <= value <= 100):
            raise DomainValidationError(f"DemandScore must be 0-100, got {value}")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @property
    def level(self) -> DemandLevel:
        return DemandLevel.from_score(self._value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DemandScore):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"DemandScore({self._value})"