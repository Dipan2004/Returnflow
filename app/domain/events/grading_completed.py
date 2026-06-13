from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class GradingCompleted:
    return_id: str
    grade: str
    confidence: float
    damage_description: str
    routed_to_human_review: bool
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="GradingCompleted", init=False)