from __future__ import annotations

from app.application.ports.image_storage_port import (
    ImageStoragePort,
    PresignedDownloadUrl,
    PresignedUploadUrl,
)
from app.domain.value_objects.image_key import ImageKey


class FakeImageStorage(ImageStoragePort):
    def __init__(self) -> None:
        self._uploaded: dict[str, set[str]] = {}

    def seed_uploaded(self, return_id: str, keys: list[str]) -> None:
        self._uploaded.setdefault(return_id, set()).update(keys)

    async def generate_upload_urls(
        self,
        return_id: str,
        count: int,
    ) -> list[PresignedUploadUrl]:
        urls: list[PresignedUploadUrl] = []
        for index in range(1, count + 1):
            key = ImageKey.pending(return_id, index)
            urls.append(
                PresignedUploadUrl(
                    url=f"https://fake-bucket.local/{key.value}?signature=fake",
                    key=key.value,
                    expires_in_seconds=300,
                )
            )
        return urls

    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 900,
    ) -> PresignedDownloadUrl:
        return PresignedDownloadUrl(
            url=f"https://fake-bucket.local/{key}?signature=fake",
            key=key,
            expires_in_seconds=expires_in,
        )

    async def list_uploaded_keys(self, return_id: str, prefix: str = "pending") -> list[str]:
        return sorted(self._uploaded.get(return_id, set()))

    async def copy_to_graded(self, return_id: str, source_keys: list[str]) -> list[str]:
        return [ImageKey.from_string(key).as_graded().value for key in source_keys]
