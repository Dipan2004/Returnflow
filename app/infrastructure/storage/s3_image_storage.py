from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from botocore.exceptions import ClientError

from app.application.ports.image_storage_port import (
    ImageStoragePort,
    PresignedDownloadUrl,
    PresignedUploadUrl,
)
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.image_key import ImageKey

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


class S3ImageStorage(ImageStoragePort):
    def __init__(self, client: S3Client, bucket: str, upload_expiry_seconds: int) -> None:
        self._client = client
        self._bucket = bucket
        self._upload_expiry_seconds = upload_expiry_seconds

    async def generate_upload_urls(
        self,
        return_id: str,
        count: int,
    ) -> list[PresignedUploadUrl]:
        results: list[PresignedUploadUrl] = []
        for index in range(1, count + 1):
            key = ImageKey.pending(return_id, index)
            try:
                url = await asyncio.to_thread(
                    self._client.generate_presigned_url,
                    "put_object",
                    Params={
                        "Bucket": self._bucket,
                        "Key": key.value,
                        "ContentType": "image/jpeg",
                    },
                    ExpiresIn=self._upload_expiry_seconds,
                )
            except ClientError as exc:
                raise InfrastructureError("S3", str(exc)) from exc

            results.append(
                PresignedUploadUrl(
                    url=url,
                    key=key.value,
                    expires_in_seconds=self._upload_expiry_seconds,
                )
            )
        return results

    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 900,
    ) -> PresignedDownloadUrl:
        try:
            url = await asyncio.to_thread(
                self._client.generate_presigned_url,
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as exc:
            raise InfrastructureError("S3", str(exc)) from exc

        return PresignedDownloadUrl(url=url, key=key, expires_in_seconds=expires_in)

    async def list_uploaded_keys(self, return_id: str, prefix: str = "pending") -> list[str]:
        full_prefix = f"{prefix}/{return_id}/"
        try:
            response = await asyncio.to_thread(
                self._client.list_objects_v2,
                Bucket=self._bucket,
                Prefix=full_prefix,
            )
        except ClientError as exc:
            raise InfrastructureError("S3", str(exc)) from exc

        return [
            obj["Key"]
            for obj in response.get("Contents", [])
            if obj["Key"] != full_prefix
        ]

    async def copy_to_graded(self, return_id: str, source_keys: list[str]) -> list[str]:
        graded_keys: list[str] = []
        for source_key in source_keys:
            graded_key = ImageKey.from_string(source_key).as_graded()
            try:
                await asyncio.to_thread(
                    self._client.copy_object,
                    Bucket=self._bucket,
                    CopySource={"Bucket": self._bucket, "Key": source_key},
                    Key=graded_key.value,
                )
            except ClientError as exc:
                raise InfrastructureError("S3", str(exc)) from exc
            graded_keys.append(graded_key.value)
        return graded_keys
