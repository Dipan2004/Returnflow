from __future__ import annotations

from ulid import ULID

from app.domain.exceptions import DomainValidationError


class ReturnId:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise DomainValidationError("ReturnId cannot be empty")
        try:
            ULID.from_str(value)
        except Exception as exc:
            raise DomainValidationError(
                f"ReturnId must be a valid ULID string, got '{value}'"
            ) from exc
        self._value = value.upper()

    @classmethod
    def generate(cls) -> ReturnId:
        return cls(str(ULID()))

    @classmethod
    def from_string(cls, value: str) -> ReturnId:
        return cls(value)

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReturnId):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"ReturnId('{self._value}')"