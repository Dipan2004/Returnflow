# app/infrastructure/persistence/in_memory_store.py
from __future__ import annotations

from datetime import datetime
from typing import Any

# Single shared dict — all in-memory repos read/write here
STORE: dict[str, dict[str, Any]] = {
    "returns": {},
    "grades": {},
    "warehouse_queue": {},
    "buyer_feed": {},
}


def add_return(return_id: str, data: dict) -> None:
    STORE["returns"][return_id] = {**data, "created_at": datetime.utcnow().isoformat()}


def get_return(return_id: str) -> dict | None:
    return STORE["returns"].get(return_id)


def update_return_status(return_id: str, status: str) -> dict | None:
    if return_id in STORE["returns"]:
        STORE["returns"][return_id]["status"] = status
        STORE["returns"][return_id]["updated_at"] = datetime.utcnow().isoformat()
        return STORE["returns"][return_id]
    return None


def get_returns_by_status(status: str) -> list[dict]:
    return [r for r in STORE["returns"].values() if r.get("status") == status]


def add_grade(return_id: str, grade_data: dict) -> None:
    STORE["grades"][return_id] = grade_data


def get_grade(return_id: str) -> dict | None:
    return STORE["grades"].get(return_id)
