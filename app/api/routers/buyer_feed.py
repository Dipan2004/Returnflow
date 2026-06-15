# app/api/routers/buyer_feed.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.infrastructure.persistence.in_memory_store import (
    get_grade,
    get_return,
    get_returns_by_status,
    update_return_status,
)

router = APIRouter(prefix="/buyer-feed", tags=["buyer_feed"])


@router.get("")
async def get_buyer_feed(buyer_id: str = Query(default="")) -> list[dict]:
    items = get_returns_by_status("AVAILABLE_FOR_RESALE")
    result = []
    for r in items:
        if buyer_id and r.get("buyer_id") == buyer_id:
            continue
        grade_data = get_grade(r["return_id"]) or {
            "grade": "B",
            "damage_description": "Good condition.",
        }
        original_price = r.get("original_price", 1000)
        resale_price = round(original_price * 0.70, 2)
        result.append(
            {
                "return_id": r["return_id"],
                "product_name": r.get("product_name", r.get("sku_id", "Unknown")),
                "sku_id": r.get("sku_id", ""),
                "grade": grade_data.get("grade", "B"),
                "condition_description": grade_data.get("damage_description", ""),
                "original_price": original_price,
                "resale_price": resale_price,
                "discount_pct": 30,
                "original_returner_id": r.get("buyer_id", ""),
            }
        )
    return result


@router.post("/{return_id}/purchase")
async def purchase_item(return_id: str, body: dict) -> dict[str, object]:
    buyer_id = body.get("buyer_id", "")
    item = get_return(return_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    if item.get("buyer_id") == buyer_id:
        raise HTTPException(status_code=403, detail="Cannot purchase your own returned item")
    update_return_status(return_id, "SOLD")
    return {"success": True, "return_id": return_id}
