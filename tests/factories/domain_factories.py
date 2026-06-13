from __future__ import annotations

from datetime import UTC, datetime

from app.domain.entities.return_request import ReturnRequest, ReturnStatus
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId


def make_return_request(
    sku_id: str = "B08N5WRWNW",
    seller_id: str = "seller_xyz",
    buyer_id: str = "buyer_abc",
    expected_image_count: int = 3,
    status: ReturnStatus = ReturnStatus.AWAITING_IMAGES,
    image_keys: list[ImageKey] | None = None,
    return_id: ReturnId | None = None,
    created_at: datetime | None = None,
) -> ReturnRequest:
    now = created_at or datetime.now(UTC)
    return ReturnRequest(
        return_id=return_id or ReturnId.generate(),
        sku_id=sku_id,
        seller_id=seller_id,
        buyer_id=buyer_id,
        expected_image_count=expected_image_count,
        created_at=now,
        status=status,
        image_keys=image_keys,
        updated_at=now,
    )


def make_pending_image_keys(return_id: str, count: int) -> list[ImageKey]:
    return [ImageKey.pending(return_id, index) for index in range(1, count + 1)]
