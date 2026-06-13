from __future__ import annotations

from app.domain.exceptions import DomainValidationError

_ALLOWED_PREFIXES = ("pending/", "graded/", "health-cards/")
_ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


class ImageKey:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise DomainValidationError("ImageKey cannot be empty")
        if not any(value.startswith(p) for p in _ALLOWED_PREFIXES):
            raise DomainValidationError(
                f"ImageKey must start with one of {_ALLOWED_PREFIXES}, got '{value}'"
            )
        if not any(value.lower().endswith(ext) for ext in _ALLOWED_EXTENSIONS):
            raise DomainValidationError(
                f"ImageKey must have one of {_ALLOWED_EXTENSIONS} extension, got '{value}'"
            )
        self._value = value

    @classmethod
    def pending(cls, return_id: str, index: int) -> ImageKey:
        return cls(f"pending/{return_id}/img_{index:03d}.jpg")

    @classmethod
    def graded(cls, return_id: str, index: int) -> ImageKey:
        return cls(f"graded/{return_id}/img_{index:03d}.jpg")

    @classmethod
    def from_string(cls, value: str) -> ImageKey:
        return cls(value)

    @property
    def value(self) -> str:
        return self._value

    @property
    def return_id(self) -> str:
        parts = self._value.split("/")
        return parts[1] if len(parts) >= 2 else ""

    def as_graded(self) -> ImageKey:
        return ImageKey(self._value.replace("pending/", "graded/", 1))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageKey):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"ImageKey('{self._value}')"