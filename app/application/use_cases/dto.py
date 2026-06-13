# app/application/use_cases/dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.return_request import ReturnStatus


@dataclass(frozen=True)
class UploadUrlDTO:
    url: str
    key: str
    expires_in_seconds: int


@dataclass(frozen=True)
class CreateReturnResult:
    return_id: str
    status: ReturnStatus
    upload_urls: list[UploadUrlDTO]
    created_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class ReturnDetailResult:
    return_id: str
    sku_id: str
    seller_id: str
    buyer_id: str
    status: ReturnStatus
    image_keys: list[str]
    expected_image_count: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ReturnStatusResult:
    return_id: str
    sku_id: str
    seller_id: str
    buyer_id: str
    status: ReturnStatus
    image_count: int
    expected_image_count: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ImageUploadCompleteResult:
    return_id: str
    status: ReturnStatus
    image_count: int
    expected_image_count: int
    all_images_received: bool


@dataclass(frozen=True)
class DamageLabelDTO:
    name: str
    confidence: float


@dataclass(frozen=True)
class ProcessGradingResult:
    return_id: str
    grade: str
    confidence: float
    damage_labels: list[DamageLabelDTO]
    damage_description: str
    routed_to_human_review: bool
    graded_at: datetime


@dataclass(frozen=True)
class ConditionGradeResult:
    return_id: str
    grade: str
    confidence: float
    damage_labels: list[DamageLabelDTO]
    damage_description: str
    routed_to_human_review: bool
    graded_at: datetime