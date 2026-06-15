# app/infrastructure/adapters/storage/stub_image_storage.py
from __future__ import annotations

from app.application.ports.image_storage_port import (
    ImageStoragePort,
    PresignedDownloadUrl,
    PresignedUploadUrl,
)


class StubImageStorage(ImageStoragePort):
    async def generate_upload_urls(
        self,
        return_id: str,
        count: int,
    ) -> list[PresignedUploadUrl]:
        results: list[PresignedUploadUrl] = []
        for i in range(1, count + 1):
            results.append(
                PresignedUploadUrl(
                    url=f"https://demo-storage.local/uploads/pending/{return_id}/img_{i:03d}.jpg",
                    key=f"pending/{return_id}/img_{i:03d}.jpg",
                    expires_in_seconds=300,
                )
            )
        return results

    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 900,
    ) -> PresignedDownloadUrl:
        return PresignedDownloadUrl(
            url=f"https://demo-storage.local/downloads/{key}",
            key=key,
            expires_in_seconds=expires_in,
        )

    async def list_uploaded_keys(self, return_id: str, prefix: str = "pending") -> list[str]:
        return [f"pending/{return_id}/img_{i:03d}.jpg" for i in range(1, 4)]

    async def copy_to_graded(self, return_id: str, source_keys: list[str]) -> list[str]:
        return [key.replace("pending/", "graded/") for key in source_keys]
