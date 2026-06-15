# app/api/routers/warehouse.py
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.routers.delivery import PRODUCTS_MAP
from app.infrastructure.persistence.in_memory_store import STORE

router = APIRouter(prefix="/warehouse", tags=["warehouse"])


class WarehouseItem(BaseModel):
    return_id: str
    sku_id: str
    product_name: str
    grade: str
    condition_description: str
    original_returner_id: str
    status: str


class ApproveResponse(BaseModel):
    return_id: str
    approved: bool
    approved_at: datetime
    resale_price: float


@router.get("/queue", response_model=list[WarehouseItem])
async def get_warehouse_queue() -> list[WarehouseItem]:
    returns = STORE.get("returns", {})
    items = []
    for rid, data in returns.items():
        if isinstance(data, dict) and data.get("status") == "PICKED_UP":
            sku = str(data.get("sku_id", ""))
            items.append(WarehouseItem(
                return_id=rid,
                sku_id=sku,
                product_name=PRODUCTS_MAP.get(sku, sku),
                grade=data.get("grade", "B"),
                condition_description=data.get("condition_description", "Good condition"),
                original_returner_id=data.get("buyer_id", ""),
                status="PICKED_UP",
            ))
    return items


@router.post("/{return_id}/approve", response_model=ApproveResponse)
async def approve_item(return_id: str) -> ApproveResponse:
    returns = STORE.setdefault("returns", {})
    resale_price = 0.0
    if return_id in returns and isinstance(returns[return_id], dict):
        returns[return_id]["status"] = "AVAILABLE_FOR_RESALE"
        original_price = float(returns[return_id].get("original_price", 999.0))
        resale_price = round(original_price * 0.70, 2)
        returns[return_id]["resale_price"] = resale_price
    return ApproveResponse(return_id=return_id, approved=True, approved_at=datetime.now(UTC), resale_price=resale_price)
