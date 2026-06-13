from __future__ import annotations

import pytest

from app.application.use_cases.get_return_status_use_case import GetReturnStatusUseCase
from app.application.use_cases.get_return_use_case import GetReturnUseCase
from app.domain.entities.return_request import ReturnStatus
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.return_id import ReturnId
from tests.factories.domain_factories import make_return_request
from tests.fakes.fake_return_repository import FakeReturnRepository


@pytest.mark.asyncio
async def test_get_return_returns_full_detail(
    fake_return_repository: FakeReturnRepository,
) -> None:
    return_request = make_return_request()
    await fake_return_repository.save(return_request)

    use_case = GetReturnUseCase(return_repository=fake_return_repository)
    result = await use_case.execute(return_id=return_request.return_id.value)

    assert result.return_id == return_request.return_id.value
    assert result.sku_id == return_request.sku_id
    assert result.status == ReturnStatus.AWAITING_IMAGES
    assert result.image_keys == []


@pytest.mark.asyncio
async def test_get_return_raises_when_missing(
    fake_return_repository: FakeReturnRepository,
) -> None:
    use_case = GetReturnUseCase(return_repository=fake_return_repository)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(return_id=ReturnId.generate().value)


@pytest.mark.asyncio
async def test_get_return_status_reports_image_progress(
    fake_return_repository: FakeReturnRepository,
) -> None:
    return_request = make_return_request(expected_image_count=3)
    await fake_return_repository.save(return_request)

    use_case = GetReturnStatusUseCase(return_repository=fake_return_repository)
    result = await use_case.execute(return_id=return_request.return_id.value)

    assert result.status == ReturnStatus.AWAITING_IMAGES
    assert result.image_count == 0
    assert result.expected_image_count == 3


@pytest.mark.asyncio
async def test_get_return_status_raises_when_missing(
    fake_return_repository: FakeReturnRepository,
) -> None:
    use_case = GetReturnStatusUseCase(return_repository=fake_return_repository)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(return_id=ReturnId.generate().value)
