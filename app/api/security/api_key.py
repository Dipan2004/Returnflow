# app/api/security/api_key.py
from __future__ import annotations

import os

from fastapi import HTTPException, Request, status

_API_KEY_HEADER = "X-API-Key"
_DEFAULT_API_KEY = "returniq-dev-key-2026"

_PUBLIC_PATHS = ("/health", "/docs", "/redoc", "/openapi.json")


def get_api_key_from_config() -> str:
    return os.environ.get("RETURNIQ_API_KEY", _DEFAULT_API_KEY)


async def verify_api_key(request: Request) -> None:
    path = request.url.path
    if any(path.startswith(p) for p in _PUBLIC_PATHS):
        return
    if request.method == "OPTIONS":
        return
    if os.environ.get("APP_ENV", "local") == "local":
        return
    api_key = request.headers.get(_API_KEY_HEADER)
    expected = get_api_key_from_config()
    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
