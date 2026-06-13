from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter

from app.api.schemas.common import HealthResponse
from app.config import get_config

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    config = get_config()
    return HealthResponse(
        status="ok",
        version=config.app_version,
        timestamp=datetime.now(UTC),
    )