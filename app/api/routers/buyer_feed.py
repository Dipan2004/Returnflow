# app/api/routers/buyer_feed.py
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.api.routers.delivery import PRODUCTS_MAP
from app.infrastructure.persistence.in_memory_store import STORE

router = APIRouter(prefix="/buyer-feed", tags=["buyer-feed"])


class BuyerFeedItem(BaseModel):
    return_id: str
    product_name: str
    grade: str
    original_price: float
    resale_price: float
    condition_description: str
    original_returner_id: str


class PurchaseRequest(BaseModel):
    buyer_id: str


class PurchaseResponse(BaseModel):
    success: bool
    return_id: str


@router.get("", response_model=list[BuyerFeedItem])
async def get_buyer_feed(
    buyer_id: str | None = Query(default=None),
    x_buyer_id: str | None = Header(default=None, alias="X-Buyer-Id"),
) -> list[BuyerFeedItem]:
    requesting_buyer = buyer_id or x_buyer_id or ""
    returns = STORE.get("returns", {})
    items = []
    for rid, data in returns.items():
        if isinstance(data, dict) and data.get("status") == "AVAILABLE_FOR_RESALE":
            original_returner = data.get("buyer_id", "")
            if requesting_buyer and original_returner == requesting_buyer:
                continue
            price = float(data.get("original_price", 999.0))
            sku = str(data.get("sku_id", ""))
            items.append(BuyerFeedItem(
                return_id=rid,
                product_name=PRODUCTS_MAP.get(sku, sku),
                grade=data.get("grade", "B"),
                original_price=price,
                resale_price=round(price * 0.7, 2),
                condition_description=data.get(
                    "condition_description",
                    "Good condition with minor wear",
                ),
                original_returner_id=original_returner,
            ))
    return items


@router.post("/{return_id}/purchase", response_model=PurchaseResponse)
async def purchase_item(return_id: str, payload: PurchaseRequest) -> PurchaseResponse:
    returns = STORE.get("returns", {})
    data = returns.get(return_id)
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=404, detail="Item not found")
    if data.get("status") != "AVAILABLE_FOR_RESALE":
        raise HTTPException(status_code=400, detail="Item is not available for purchase")
    if data.get("buyer_id") == payload.buyer_id:
        raise HTTPException(status_code=403, detail="Cannot purchase your own returned item")
    data["status"] = "SOLD"
    data["purchaser_id"] = payload.buyer_id
    return PurchaseResponse(success=True, return_id=return_id)
