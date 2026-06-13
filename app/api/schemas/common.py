from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        frozen=True,
    )


class ErrorDetail(BaseSchema):
    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseSchema):
    errors: list[ErrorDetail]
    request_id: str | None = None


class HealthResponse(BaseSchema):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseSchema):
    items: list[BaseModel]
    total: int
    page: int
    page_size: int
    has_next: bool