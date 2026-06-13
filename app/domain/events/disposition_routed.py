from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class DispositionRouted:
    return_id: str
    route: str
    grade: str
    recovery_value: Decimal
    value_delta: Decimal
    fraud_flagged: bool
    matched_buyer_id: str | None
    distance_km: float | None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = field(default="DispositionRouted", init=False)
