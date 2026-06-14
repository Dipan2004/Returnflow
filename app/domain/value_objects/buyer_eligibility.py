# app/domain/value_objects/buyer_eligibility.py | 22 lines
from __future__ import annotations

from enum import StrEnum


class BuyerEligibility(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"

    @property
    def is_eligible(self) -> bool:
        return self == BuyerEligibility.ELIGIBLE