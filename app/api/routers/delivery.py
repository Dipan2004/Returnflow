# app/api/routers/delivery.py
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.infrastructure.persistence.in_memory_store import (
    add_return,
    get_grade,
    get_return,
    get_returns_by_status,
    update_return_status,
)

router = APIRouter(prefix="/delivery", tags=["delivery"])

DEMO_GRADE_MAP = {
    "demo-r001": {
        "grade": "A",
        "confidence": 92.0,
        "damage_description": "Minor toe-box scuff. Soles clean.",
    },
    "demo-r002": {
        "grade": "B",
        "confidence": 85.0,
        "damage_description": "Light ear-pad wear. Audio perfect.",
    },
    "demo-r003": {
        "grade": "C",
        "confidence": 78.0,
        "damage_description": "Visible pilling on fabric. Wearable.",
    },
}


@router.get("/queue")
async def get_delivery_queue() -> list[dict]:
    real_items = get_returns_by_status("PENDING_PICKUP")
    result = []
    for r in real_items:
        grade_data = get_grade(r["return_id"]) or {}
        raw_name = r.get("product_name", r.get("sku_id", "Unknown"))
        from app.api.routers.returns import _resolve_product_name
        product_name = (
            raw_name if raw_name != r.get("sku_id") else
            _resolve_product_name(r.get("sku_id", ""))
        )
        result.append(
            {
                "return_id": r["return_id"],
                "product_name": product_name,
                "sku_id": r.get("sku_id", ""),
                "grade": grade_data.get("grade", r.get("grade", "B")),
                "pickup_address": r.get(
                    "pickup_address", "Customer Address"
                ),
                "pickup_window": r.get(
                    "pickup_window", "Tomorrow, 10 AM - 2 PM"
                ),
                "status": "PENDING_PICKUP",
                "buyer_id": r.get("buyer_id", ""),
                "image_count": r.get("image_count", 0),
            }
        )
    if not result:
        return []
    return result


@router.post("/{return_id}/confirm")
async def confirm_pickup(
    return_id: str, body: dict | None = None,
) -> dict[str, object]:
    if body is None:
        body = {}
    item = get_return(return_id)
    if not item:
        add_return(
            return_id,
            {
                "return_id": return_id,
                "product_name": body.get("product_name", "Unknown"),
                "sku_id": body.get("sku_id", ""),
                "buyer_id": body.get("agent_id", "agent"),
                "status": "PENDING_PICKUP",
            },
        )
    update_return_status(return_id, "PICKED_UP")
    return {
        "return_id": return_id,
        "confirmed": True,
        "confirmed_at": datetime.utcnow().isoformat(),
    }
