# app/api/routers/delivery.py
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/delivery", tags=["delivery"])


class DeliveryQueueItem(BaseModel):
    return_id: str
    product: str
    grade: str
    pickup_window: str
    address: str
    route: str


class HandoffConfirmResponse(BaseModel):
    return_id: str
    confirmed: bool
    confirmed_at: datetime


@router.get("/queue", response_model=list[DeliveryQueueItem])
async def get_delivery_queue() -> list[DeliveryQueueItem]:
    return [
        DeliveryQueueItem(
            return_id="demo-r001",
            product="Nike Air Max 270",
            grade="A",
            pickup_window="Today, 10 AM - 2 PM",
            address="Patia, Bhubaneswar, 751024",
            route="P2P",
        ),
        DeliveryQueueItem(
            return_id="demo-r002",
            product="boAt Rockerz 450",
            grade="B",
            pickup_window="Today, 2 PM - 6 PM",
            address="Saheed Nagar, Bhubaneswar, 751007",
            route="REFURBISH",
        ),
        DeliveryQueueItem(
            return_id="demo-r003",
            product="Puma T-Shirt",
            grade="C",
            pickup_window="Tomorrow, 10 AM - 2 PM",
            address="Chandrasekharpur, Bhubaneswar, 751023",
            route="DONATE",
        ),
    ]
