# app/api/routers/delivery.py
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.domain.entities.return_request import ReturnRequest
from app.infrastructure.persistence.in_memory_store import STORE

router = APIRouter(prefix="/delivery", tags=["delivery"])

PRODUCTS_MAP = {
    "1": "Nike Air Max 270",
    "2": "Adidas Ultraboost 22",
    "3": "Puma RS-X Reinvention",
    "4": "New Balance 574 Core",
    "5": "Reebok Classic Leather",
    "6": "boAt Rockerz 450",
    "7": "Sony WH-1000XM5",
    "8": "JBL Flip 6",
    "9": "Realme Buds Air 5 Pro",
    "10": "OnePlus Nord Buds 2",
    "11": "Levi's 511 Slim Fit Jeans",
    "12": "H&M Regular Fit T-Shirt",
    "13": "Zara Textured Blazer",
    "14": "US Polo Assn. Polo Shirt",
    "15": "Philips LED Desk Lamp",
    "16": "Havells Instanio Prime Water Heater",
    "17": "Milton Thermosteel Flask 1L",
    "18": "Atomic Habits by James Clear",
    "19": "Wildcraft Laptop Backpack 35L",
    "20": "Fossil Gen 6 Smartwatch",
    "21": "Casio G-Shock DW-5600",
    "22": "American Tourister Trolley Bag",
    "23": "Levi's Denim Jacket",
    "24": "Philips Air Purifier AC1215",
}


class DeliveryQueueItem(BaseModel):
    return_id: str
    sku_id: str
    product_name: str
    grade: str
    pickup_window: str
    pickup_address: str
    status: str


class DeliveryConfirmResponse(BaseModel):
    return_id: str
    confirmed: bool
    confirmed_at: datetime


@router.get("/queue", response_model=list[DeliveryQueueItem])
async def get_delivery_queue() -> list[DeliveryQueueItem]:
    returns = STORE.get("returns", {})
    live_items = []
    for rid, data in returns.items():
        if isinstance(data, dict) and data.get("status") == "PENDING_PICKUP":
            sku = str(data.get("sku_id", ""))
            live_items.append(DeliveryQueueItem(
                return_id=rid,
                sku_id=sku,
                product_name=PRODUCTS_MAP.get(sku, sku),
                grade=data.get("grade", "B"),
                pickup_window=data.get("pickup_window", "Today, 10 AM – 2 PM"),
                pickup_address=data.get("address", "Patia, Bhubaneswar, 751024"),
                status="PENDING_PICKUP",
            ))
        elif isinstance(data, ReturnRequest) and data.status.value == "PENDING_PICKUP":
            sku = data.sku_id
            live_items.append(DeliveryQueueItem(
                return_id=data.return_id.value,
                sku_id=sku,
                product_name=PRODUCTS_MAP.get(sku, sku),
                grade="B",
                pickup_window="Today, 10 AM – 2 PM",
                pickup_address="Patia, Bhubaneswar, 751024",
                status="PENDING_PICKUP",
            ))
    return live_items


@router.post("/{return_id}/confirm", response_model=DeliveryConfirmResponse)
async def confirm_delivery(return_id: str) -> DeliveryConfirmResponse:
    returns = STORE.setdefault("returns", {})
    if return_id in returns:
        data = returns[return_id]
        if isinstance(data, dict):
            data["status"] = "PICKED_UP"
        elif isinstance(data, ReturnRequest):
            returns[return_id] = {
                "sku_id": data.sku_id,
                "buyer_id": data.buyer_id,
                "grade": "B",
                "status": "PICKED_UP",
                "original_price": 999.0,
                "address": "Patia, Bhubaneswar, 751024",
            }
    return DeliveryConfirmResponse(return_id=return_id, confirmed=True, confirmed_at=datetime.now(UTC))
