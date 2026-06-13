from __future__ import annotations

import secrets
import time

from app.domain.exceptions import DomainValidationError

_CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_ULID_LENGTH = 26


def _encode_base32(value: int, length: int) -> str:
    chars: list[str] = []
    for _ in range(length):
        value, remainder = divmod(value, 32)
        chars.append(_CROCKFORD_BASE32[remainder])
    return "".join(reversed(chars))


def _generate_ulid() -> str:
    timestamp_ms = int(time.time() * 1000)
    random_bits = secrets.randbits(80)
    return f"{_encode_base32(timestamp_ms, 10)}{_encode_base32(random_bits, 16)}"


class ReturnId:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise DomainValidationError("ReturnId cannot be empty")
        normalized = value.strip().upper()
        self._value = normalized

    @classmethod
    def generate(cls) -> ReturnId:
        return cls(_generate_ulid())

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
