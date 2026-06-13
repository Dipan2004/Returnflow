from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.entities.return_request import ReturnRequest, ReturnStatus
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_RETURN_REQUEST = "RETURN_REQUEST"


def return_request_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def return_request_sk() -> str:
    return "REQUEST"


def seller_gsi_pk(seller_id: str) -> str:
    return f"SELLER#{seller_id}"


def buyer_gsi_pk(buyer_id: str) -> str:
    return f"BUYER#{buyer_id}"


def return_gsi_sk(created_at: datetime, return_id: ReturnId) -> str:
    return f"RETURN#{created_at.isoformat()}#{return_id.value}"


def to_item(return_request: ReturnRequest) -> dict[str, Any]:
    return {
        "PK": return_request_pk(return_request.return_id),
        "SK": return_request_sk(),
        "GSI1PK": seller_gsi_pk(return_request.seller_id),
        "GSI1SK": return_gsi_sk(return_request.created_at, return_request.return_id),
        "GSI2PK": buyer_gsi_pk(return_request.buyer_id),
        "GSI2SK": return_gsi_sk(return_request.created_at, return_request.return_id),
        "entity_type": ENTITY_TYPE_RETURN_REQUEST,
        "return_id": return_request.return_id.value,
        "sku_id": return_request.sku_id,
        "seller_id": return_request.seller_id,
        "buyer_id": return_request.buyer_id,
        "expected_image_count": return_request.expected_image_count,
        "status": return_request.status.value,
        "image_keys": [key.value for key in return_request.image_keys],
        "created_at": return_request.created_at.isoformat(),
        "updated_at": return_request.updated_at.isoformat(),
    }


def from_item(item: dict[str, Any]) -> ReturnRequest:
    return ReturnRequest(
        return_id=ReturnId.from_string(str(item["return_id"])),
        sku_id=str(item["sku_id"]),
        seller_id=str(item["seller_id"]),
        buyer_id=str(item["buyer_id"]),
        expected_image_count=int(item["expected_image_count"]),
        created_at=datetime.fromisoformat(str(item["created_at"])),
        status=ReturnStatus(str(item["status"])),
        image_keys=[ImageKey.from_string(str(key)) for key in item.get("image_keys", [])],
        updated_at=datetime.fromisoformat(str(item["updated_at"])),
    )
