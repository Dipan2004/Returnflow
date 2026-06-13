from __future__ import annotations

from datetime import timedelta

from app.application.ports.image_storage_port import ImageStoragePort
from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.dto import CreateReturnResult, UploadUrlDTO
from app.domain.entities.return_request import ReturnRequest
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CreateReturnUseCase:
    def __init__(
        self,
        return_repository: ReturnRepository,
        image_storage: ImageStoragePort,
    ) -> None:
        self._return_repository = return_repository
        self._image_storage = image_storage

    async def execute(
        self,
        sku_id: str,
        seller_id: str,
        buyer_id: str,
        image_count: int,
    ) -> CreateReturnResult:
        return_request = ReturnRequest.create(
            sku_id=sku_id,
            seller_id=seller_id,
            buyer_id=buyer_id,
            expected_image_count=image_count,
        )

        upload_urls = await self._image_storage.generate_upload_urls(
            return_id=return_request.return_id.value,
            count=image_count,
        )

        await self._return_repository.save(return_request)

        logger.info(
            "Return request created",
            return_id=return_request.return_id.value,
            sku_id=sku_id,
            seller_id=seller_id,
            buyer_id=buyer_id,
            image_count=image_count,
        )

        max_expiry = max((url.expires_in_seconds for url in upload_urls), default=0)
        expires_at = return_request.created_at + timedelta(seconds=max_expiry)

        return CreateReturnResult(
            return_id=return_request.return_id.value,
            status=return_request.status,
            upload_urls=[
                UploadUrlDTO(url=u.url, key=u.key, expires_in_seconds=u.expires_in_seconds)
                for u in upload_urls
            ],
            created_at=return_request.created_at,
            expires_at=expires_at,
        )
