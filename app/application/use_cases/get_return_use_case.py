from __future__ import annotations

from app.application.ports.return_repository import ReturnRepository
from app.application.use_cases.dto import ReturnDetailResult
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId


class GetReturnUseCase:
    def __init__(self, return_repository: ReturnRepository) -> None:
        self._return_repository = return_repository

    async def execute(self, return_id: str) -> ReturnDetailResult:
        identifier = ReturnId.from_string(return_id)
        return_request = await self._return_repository.get_by_id(identifier)

        if return_request is None:
            raise EntityNotFoundError(entity="ReturnRequest", identifier=return_id)

        return ReturnDetailResult(
            return_id=return_request.return_id.value,
            sku_id=return_request.sku_id,
            seller_id=return_request.seller_id,
            buyer_id=return_request.buyer_id,
            status=return_request.status,
            image_keys=[key.value for key in return_request.image_keys],
            expected_image_count=return_request.expected_image_count,
            created_at=return_request.created_at,
            updated_at=return_request.updated_at,
        )
