from __future__ import annotations

from datetime import datetime

from pydantic import Field, field_validator

from app.api.schemas.common import BaseSchema
from app.domain.entities.return_request import ReturnStatus


class CreateReturnRequest(BaseSchema):
    sku_id: str = Field(min_length=1, max_length=100)
    seller_id: str = Field(min_length=1, max_length=100)
    buyer_id: str = Field(min_length=1, max_length=100)
    image_count: int = Field(default=3, ge=1, le=10)

    @field_validator("sku_id", "seller_id", "buyer_id", mode="before")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        stripped = str(v).strip()
        if not stripped:
            raise ValueError("Field cannot be blank")
        return stripped


class UploadUrl(BaseSchema):
    url: str
    key: str
    expires_in_seconds: int


class CreateReturnResponse(BaseSchema):
    return_id: str
    status: ReturnStatus
    upload_urls: list[UploadUrl]
    expires_at: datetime
    created_at: datetime


class ReturnStatusResponse(BaseSchema):
    return_id: str
    sku_id: str
    seller_id: str
    buyer_id: str
    status: ReturnStatus
    image_count: int
    expected_image_count: int
    created_at: datetime
    updated_at: datetime


class ImageUploadCompleteRequest(BaseSchema):
    image_keys: list[str] = Field(min_length=1, max_length=10)

    @field_validator("image_keys")
    @classmethod
    def validate_keys_not_empty(cls, v: list[str]) -> list[str]:
        for key in v:
            if not key or not key.strip():
                raise ValueError("Image keys cannot be empty strings")
        return v


class ReturnDetailResponse(BaseSchema):
    return_id: str
    sku_id: str
    seller_id: str
    buyer_id: str
    status: ReturnStatus
    image_keys: list[str]
    expected_image_count: int
    created_at: datetime
    updated_at: datetime


class ImageUploadCompleteResponse(BaseSchema):
    return_id: str
    status: ReturnStatus
    image_count: int
    expected_image_count: int
    all_images_received: bool