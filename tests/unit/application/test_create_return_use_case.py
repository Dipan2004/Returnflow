from __future__ import annotations

import pytest

from app.application.use_cases.create_return_use_case import CreateReturnUseCase
from app.domain.entities.return_request import ReturnStatus
from tests.fakes.fake_image_storage import FakeImageStorage
from tests.fakes.fake_return_repository import FakeReturnRepository


@pytest.mark.asyncio
async def test_create_return_persists_request_and_returns_upload_urls(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    use_case = CreateReturnUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    result = await use_case.execute(
        sku_id="B08N5WRWNW",
        seller_id="seller_xyz",
        buyer_id="buyer_abc",
        image_count=3,
    )

    assert result.status == ReturnStatus.AWAITING_IMAGES
    assert len(result.upload_urls) == 3
    assert all(url.key.startswith(f"pending/{result.return_id}/") for url in result.upload_urls)
    assert result.expires_at > result.created_at

    stored = await fake_return_repository.get_by_id_str(result.return_id)
    assert stored is not None
    assert stored.sku_id == "B08N5WRWNW"
    assert stored.expected_image_count == 3


@pytest.mark.asyncio
async def test_create_return_respects_requested_image_count(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    use_case = CreateReturnUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    result = await use_case.execute(
        sku_id="SKU-1",
        seller_id="seller_1",
        buyer_id="buyer_1",
        image_count=5,
    )

    assert len(result.upload_urls) == 5
