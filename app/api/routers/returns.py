from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.schemas.return_schemas import (
    CreateReturnRequest,
    CreateReturnResponse,
    ImageUploadCompleteRequest,
    ImageUploadCompleteResponse,
    ReturnDetailResponse,
    UploadUrl,
)
from app.application.use_cases.complete_image_upload_use_case import (
    CompleteImageUploadUseCase,
)
from app.application.use_cases.create_return_use_case import CreateReturnUseCase
from app.application.use_cases.get_return_use_case import GetReturnUseCase
from app.container import Container
from app.infrastructure.persistence.in_memory_store import (
    add_return,
    get_grade,
    get_return as get_return_from_store,
    update_return_status as update_return_status_in_store,
)

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("", response_model=CreateReturnResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_return(
    payload: CreateReturnRequest,
    use_case: CreateReturnUseCase = Depends(Provide[Container.create_return_use_case]),
) -> CreateReturnResponse:
    result = await use_case.execute(
        sku_id=payload.sku_id,
        seller_id=payload.seller_id,
        buyer_id=payload.buyer_id,
        image_count=payload.image_count,
    )

    add_return(
        result.return_id,
        {
            "return_id": result.return_id,
            "sku_id": payload.sku_id,
            "buyer_id": payload.buyer_id,
            "seller_id": payload.seller_id,
            "status": "PENDING_PICKUP",
            "image_count": getattr(payload, "image_count", 0),
            "reason": getattr(payload, "reason", ""),
            "product_name": payload.sku_id,
            "pickup_address": getattr(payload, "pickup_address", "Customer Address, Bhubaneswar"),
            "pickup_window": "Tomorrow, 10 AM - 2 PM",
            "original_price": getattr(payload, "original_price", 0),
        },
    )

    return CreateReturnResponse(
        return_id=result.return_id,
        status=result.status,
        upload_urls=[
            UploadUrl(url=u.url, key=u.key, expires_in_seconds=u.expires_in_seconds)
            for u in result.upload_urls
        ],
        expires_at=result.expires_at,
        created_at=result.created_at,
    )


@router.get("/{return_id}", response_model=ReturnDetailResponse)
@inject
async def get_return(
    return_id: str,
    use_case: GetReturnUseCase = Depends(Provide[Container.get_return_use_case]),
) -> ReturnDetailResponse:
    result = await use_case.execute(return_id=return_id)
    return ReturnDetailResponse(
        return_id=result.return_id,
        sku_id=result.sku_id,
        seller_id=result.seller_id,
        buyer_id=result.buyer_id,
        status=result.status,
        image_keys=result.image_keys,
        expected_image_count=result.expected_image_count,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/{return_id}/status")
async def get_return_status(return_id: str) -> dict[str, str]:
    item = get_return_from_store(return_id)
    if not item:
        return {"return_id": return_id, "status": "NOT_FOUND"}
    return {
        "return_id": return_id,
        "status": item.get("status", "UNKNOWN"),
        "updated_at": item.get("updated_at", ""),
    }


@router.post("/{return_id}/images/complete", response_model=ImageUploadCompleteResponse)
@inject
async def complete_image_upload(
    return_id: str,
    payload: ImageUploadCompleteRequest,
    use_case: CompleteImageUploadUseCase = Depends(
        Provide[Container.complete_image_upload_use_case]
    ),
) -> ImageUploadCompleteResponse:
    result = await use_case.execute(return_id=return_id, image_keys=payload.image_keys)
    return ImageUploadCompleteResponse(
        return_id=result.return_id,
        status=result.status,
        image_count=result.image_count,
        expected_image_count=result.expected_image_count,
        all_images_received=result.all_images_received,
    )


class UpdateStatusRequest(BaseModel):
    status: str = Field(min_length=1, max_length=50)


@router.patch("/{return_id}/status")
async def patch_return_status(return_id: str, payload: UpdateStatusRequest) -> dict:
    updated = update_return_status_in_store(return_id, payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Return not found")
    return updated


class DemoStatusResponse(BaseModel):
    return_id: str
    status: str
    sku_id: str
    product_name: str
    grade: str


@router.get("/{return_id}/flow-status", response_model=DemoStatusResponse)
async def get_return_flow_status(return_id: str) -> DemoStatusResponse:
    data = get_return_from_store(return_id)
    grade_data = get_grade(return_id) or {}
    if data:
        sku = str(data.get("sku_id", ""))
        return DemoStatusResponse(
            return_id=return_id,
            status=data.get("status", "UNKNOWN"),
            sku_id=sku,
            product_name=data.get("product_name", sku),
            grade=grade_data.get("grade", ""),
        )
    return DemoStatusResponse(
        return_id=return_id,
        status="UNKNOWN",
        sku_id="",
        product_name="",
        grade="",
    )
