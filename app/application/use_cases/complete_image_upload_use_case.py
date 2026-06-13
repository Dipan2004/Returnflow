from __future__ import annotations

from app.application.ports.image_storage_port import ImageStoragePort
from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.dto import ImageUploadCompleteResult
from app.domain.exceptions import EntityNotFoundError, ImageUploadError
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CompleteImageUploadUseCase:
    def __init__(
        self,
        return_repository: ReturnRepository,
        image_storage: ImageStoragePort,
    ) -> None:
        self._return_repository = return_repository
        self._image_storage = image_storage

    async def execute(self, return_id: str, image_keys: list[str]) -> ImageUploadCompleteResult:
        identifier = ReturnId.from_string(return_id)
        return_request = await self._return_repository.get_by_id(identifier)

        if return_request is None:
            raise EntityNotFoundError(entity="ReturnRequest", identifier=return_id)

        parsed_keys: list[ImageKey] = []
        for raw_key in image_keys:
            key = ImageKey.from_string(raw_key)
            if key.return_id != return_request.return_id.value:
                raise ImageUploadError(
                    f"Image key '{raw_key}' does not belong to return '{return_id}'"
                )
            parsed_keys.append(key)

        uploaded_keys = set(
            await self._image_storage.list_uploaded_keys(return_request.return_id.value)
        )
        for key in parsed_keys:
            if key.value not in uploaded_keys:
                raise ImageUploadError(
                    f"Image key '{key.value}' was not found in object storage"
                )

        for key in parsed_keys:
            return_request.add_image_key(key)

        await self._return_repository.save(return_request)

        logger.info(
            "Image upload completion recorded",
            return_id=return_id,
            image_count=len(return_request.image_keys),
            status=return_request.status.value,
        )

        return ImageUploadCompleteResult(
            return_id=return_request.return_id.value,
            status=return_request.status,
            image_count=len(return_request.image_keys),
            expected_image_count=return_request.expected_image_count,
            all_images_received=return_request.all_images_received(),
        )
