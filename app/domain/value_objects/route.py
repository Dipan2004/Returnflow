from __future__ import annotations

from enum import Enum

from app.domain.exceptions import DomainValidationError


class Route(str, Enum):
    P2P = "P2P"
    RESELL = "RESELL"
    REFURBISH = "REFURBISH"
    DONATE = "DONATE"
    SCRAP = "SCRAP"
    HUMAN_REVIEW = "HUMAN_REVIEW"

    @classmethod
    def from_string(cls, value: str) -> Route:
        try:
            return cls(value.upper())
        except ValueError:
            valid = ", ".join(m.value for m in cls)
            raise DomainValidationError(
                f"Invalid route '{value}'. Must be one of: {valid}"
            )

    @property
    def generates_revenue(self) -> bool:
        return self in (Route.P2P, Route.RESELL, Route.REFURBISH)

    @property
    def requires_logistics(self) -> bool:
        return self in (Route.P2P, Route.RESELL, Route.REFURBISH, Route.DONATE)

    @property
    def display_label(self) -> str:
        labels: dict[Route, str] = {
            Route.P2P: "Peer-to-Peer Sale",
            Route.RESELL: "Amazon Resell",
            Route.REFURBISH: "Amazon Certified Refurbished",
            Route.DONATE: "Donate to NGO",
            Route.SCRAP: "Responsible Disposal",
            Route.HUMAN_REVIEW: "Manual Review Required",
        }
        return labels[self]