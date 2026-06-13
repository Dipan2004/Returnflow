from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ReturnSubmitted:
    return_id: str
    sku_id: str
    seller_id: str
    buyer_id: str
    expected_image_count: int
    image_keys: tuple[str, ...]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = field(default="ReturnSubmitted", init=False)