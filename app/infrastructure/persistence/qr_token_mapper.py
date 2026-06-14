# app/infrastructure/persistence/qr_token_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.qr_token import QRToken
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_QR_TOKEN = "QR_TOKEN"


def qr_token_pk(token: str) -> str:
    return f"QR#{token}"


def qr_token_sk() -> str:
    return "META"


def to_item(qr_token: QRToken) -> dict[str, Any]:
    item: dict[str, Any] = {
        "PK": qr_token_pk(qr_token.token),
        "SK": qr_token_sk(),
        "entity_type": ENTITY_TYPE_QR_TOKEN,
        "token": qr_token.token,
        "return_id": qr_token.return_id.value,
        "created_at": qr_token.created_at.isoformat(),
        "ttl_hours": qr_token.ttl_hours,
        "scanned": qr_token.scanned,
    }
    if qr_token.scanned_at:
        item["scanned_at"] = qr_token.scanned_at.isoformat()
    if qr_token.scanned_by:
        item["scanned_by"] = qr_token.scanned_by
    return item


def from_item(item: dict[str, Any]) -> QRToken:
    scanned_at = None
    if item.get("scanned_at"):
        scanned_at = datetime.fromisoformat(item["scanned_at"]).replace(tzinfo=UTC)
    return QRToken(
        token=item["token"],
        return_id=ReturnId(item["return_id"]),
        created_at=datetime.fromisoformat(item["created_at"]).replace(tzinfo=UTC),
        ttl_hours=int(item["ttl_hours"]),
        scanned=bool(item.get("scanned", False)),
        scanned_at=scanned_at,
        scanned_by=item.get("scanned_by"),
    )
