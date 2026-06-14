# app/infrastructure/adapters/qr_storage/local_qr_storage.py
from __future__ import annotations

from app.application.ports.qr_storage_port import QRCodeStoragePort


class LocalQRCodeStorage(QRCodeStoragePort):
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._base_url = base_url.rstrip("/")
        self._store: dict[str, bytes] = {}

    async def store_qr_image(self, key: str, image_data: bytes) -> str:
        self._store[key] = image_data
        return f"{self._base_url}/static/{key}"

    async def get_image_url(self, key: str) -> str:
        return f"{self._base_url}/static/{key}"
