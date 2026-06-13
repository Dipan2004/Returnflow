from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PresignedUploadUrl:
    url: str
    key: str
    expires_in_seconds: int


@dataclass(frozen=True)
class PresignedDownloadUrl:
    url: str
    key: str
    expires_in_seconds: int


class ImageStoragePort(ABC):
    @abstractmethod
    async def generate_upload_urls(
        self,
        return_id: str,
        count: int,
    ) -> list[PresignedUploadUrl]: ...

    @abstractmethod
    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 900,
    ) -> PresignedDownloadUrl: ...

    @abstractmethod
    async def list_uploaded_keys(self, return_id: str, prefix: str = "pending") -> list[str]: ...

    @abstractmethod
    async def copy_to_graded(self, return_id: str, source_keys: list[str]) -> list[str]: ...