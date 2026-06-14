# tests/fakes/fake_qr_storage_port.py
from __future__ import annotations

from app.application.ports.qr_storage_port import QRCodeStoragePort


class FakeQRCodeStoragePort(QRCodeStoragePort):
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    async def store_qr_image(self, key: str, image_data: bytes) -> str:
        self._store[key] = image_data
        return f"http://fake/{key}"

    async def get_image_url(self, key: str) -> str:
        return f"http://fake/{key}"

    def has_image(self, key: str) -> bool:
        return key in self._store
