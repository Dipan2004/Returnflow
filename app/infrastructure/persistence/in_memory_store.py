# app/infrastructure/persistence/in_memory_store.py
from __future__ import annotations

from datetime import datetime
from typing import Any

STORE: dict[str, dict[str, Any]] = {
    "returns": {},
    "grades": {},
    "warehouse_queue": {},
    "buyer_feed": {},
}


def add_return(return_id: str, data: dict[str, Any]) -> None:
    STORE["returns"][return_id] = {
        **data,
        "created_at": datetime.utcnow().isoformat(),
    }


def get_return(return_id: str) -> dict[str, Any] | None:
    result: Any = STORE["returns"].get(return_id)
    if result is None:
        return None
    return dict(result)


def update_return_status(
    return_id: str, status: str,
) -> dict[str, Any] | None:
    if return_id in STORE["returns"]:
        STORE["returns"][return_id]["status"] = status
        STORE["returns"][return_id]["updated_at"] = (
            datetime.utcnow().isoformat()
        )
        return dict(STORE["returns"][return_id])
    return None


def get_returns_by_status(status: str) -> list[dict[str, Any]]:
    return [
        dict(r) for r in STORE["returns"].values()
        if r.get("status") == status
    ]


def add_grade(return_id: str, grade_data: dict[str, Any]) -> None:
    STORE["grades"][return_id] = grade_data
    if return_id in STORE["returns"]:
        STORE["returns"][return_id]["grade"] = grade_data.get("grade", "")


def get_grade(return_id: str) -> dict[str, Any] | None:
    result: Any = STORE["grades"].get(return_id)
    if result is None:
        return None
    return dict(result)
