from __future__ import annotations

from enum import StrEnum

from app.domain.exceptions import DomainValidationError


class Grade(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    DONATE = "DONATE"
    SCRAP = "SCRAP"

    @classmethod
    def from_string(cls, value: str) -> Grade:
        try:
            return cls(value.upper())
        except ValueError as exc:
            valid = ", ".join(m.value for m in cls)
            raise DomainValidationError(
                f"Invalid grade '{value}'. Must be one of: {valid}"
            ) from exc

    @property
    def is_resaleable(self) -> bool:
        return self in (Grade.A, Grade.B)

    @property
    def is_p2p_eligible(self) -> bool:
        return self == Grade.A

    @property
    def display_label(self) -> str:
        labels: dict[Grade, str] = {
            Grade.A: "Excellent — No visible damage",
            Grade.B: "Good — Minor cosmetic damage",
            Grade.C: "Fair — Significant damage",
            Grade.DONATE: "Donate — Not suitable for resale",
            Grade.SCRAP: "Scrap — End of life",
        }
        return labels[self]