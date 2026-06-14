# app/application/ports/qr_storage_port.py
from __future__ import annotations

from abc import ABC, abstractmethod


class QRCodeStoragePort(ABC):
    @abstractmethod
    async def store_qr_image(self, key: str, image_data: bytes) -> str: ...

    @abstractmethod
    async def get_image_url(self, key: str) -> str: ...
