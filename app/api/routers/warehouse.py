# app/api/routers/warehouse.py
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.infrastructure.persistence.in_memory_store import (
    get_grade,
    get_return,
    get_returns_by_status,
    update_return_status,
)

router = APIRouter(prefix="/warehouse", tags=["warehouse"])


@router.get("/queue")
async def get_warehouse_queue() -> list[dict]:
    items = get_returns_by_status("PICKED_UP")
    result = []
    for r in items:
        grade_data = get_grade(r["return_id"]) or {
            "grade": "B",
            "confidence": 85.0,
            "damage_description": "Awaiting re-grade.",
        }
        result.append(
            {
                "return_id": r["return_id"],
                "product_name": r.get("product_name", r.get("sku_id", "Unknown")),
                "sku_id": r.get("sku_id", ""),
                "grade": grade_data.get("grade", "B"),
                "confidence": grade_data.get("confidence", 85.0),
                "condition_description": grade_data.get("damage_description", ""),
                "original_returner_id": r.get("buyer_id", ""),
                "original_price": r.get("original_price", 0),
                "status": "PICKED_UP",
            }
        )
    return result


@router.post("/{return_id}/approve")
async def approve_for_resale(return_id: str) -> dict[str, object]:
    item = get_return(return_id)
    if not item:
        raise HTTPException(status_code=404, detail="Return not found")
    update_return_status(return_id, "AVAILABLE_FOR_RESALE")
    original_price = item.get("original_price", 1000)
    resale_price = round(original_price * 0.70, 2)
    return {
        "approved": True,
        "return_id": return_id,
        "resale_price": resale_price,
        "approved_at": datetime.utcnow().isoformat(),
    }
