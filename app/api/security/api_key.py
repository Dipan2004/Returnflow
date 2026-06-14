# app/api/security/api_key.py
from __future__ import annotations

import os

from fastapi import HTTPException, Request, status

_API_KEY_HEADER = "X-API-Key"
_DEFAULT_API_KEY = "returniq-dev-key-2026"


def get_api_key_from_config() -> str:
    return os.environ.get("RETURNIQ_API_KEY", _DEFAULT_API_KEY)


async def verify_api_key(request: Request) -> None:
    if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
        return
    if request.url.path.startswith("/health"):
        return
    api_key = request.headers.get(_API_KEY_HEADER)
    expected = get_api_key_from_config()
    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
