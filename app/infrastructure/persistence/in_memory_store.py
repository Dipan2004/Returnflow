# app/infrastructure/persistence/in_memory_store.py
from __future__ import annotations

from typing import Any

STORE: dict[str, dict[str, Any]] = {}
