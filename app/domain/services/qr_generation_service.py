# app/domain/services/qr_generation_service.py
from __future__ import annotations

import io

import qrcode

from app.domain.entities.qr_token import QRToken
from app.domain.value_objects.return_id import ReturnId


class QRCodeGenerationService:
    def __init__(self, base_url: str, ttl_hours: int = 48) -> None:
        self._base_url = base_url.rstrip("/")
        self._ttl_hours = ttl_hours

    def generate_token(self, return_id: ReturnId) -> QRToken:
        return QRToken.generate(return_id=return_id, ttl_hours=self._ttl_hours)

    def build_verification_url(self, token: str) -> str:
        return f"{self._base_url}/verify/{token}"

    def generate_qr_image(self, verification_url: str) -> bytes:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def build_storage_key(self, return_id: ReturnId) -> str:
        return f"health-cards/{return_id.value}/qr.png"
