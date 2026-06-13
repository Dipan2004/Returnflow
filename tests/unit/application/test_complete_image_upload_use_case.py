from __future__ import annotations

import pytest

from app.application.use_cases.complete_image_upload_use_case import (
    CompleteImageUploadUseCase,
)
from app.domain.entities.return_request import ReturnStatus
from app.domain.exceptions import EntityNotFoundError, ImageUploadError
from app.domain.value_objects.return_id import ReturnId
from tests.factories.domain_factories import make_pending_image_keys, make_return_request
from tests.fakes.fake_image_storage import FakeImageStorage
from tests.fakes.fake_return_repository import FakeReturnRepository


@pytest.mark.asyncio
async def test_complete_image_upload_transitions_to_images_received(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    return_request = make_return_request(expected_image_count=3)
    await fake_return_repository.save(return_request)

    keys = make_pending_image_keys(return_request.return_id.value, 3)
    fake_image_storage.seed_uploaded(
        return_request.return_id.value, [k.value for k in keys]
    )

    use_case = CompleteImageUploadUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    result = await use_case.execute(
        return_id=return_request.return_id.value,
        image_keys=[k.value for k in keys],
    )

    assert result.status == ReturnStatus.IMAGES_RECEIVED
    assert result.image_count == 3
    assert result.all_images_received is True

    stored = await fake_return_repository.get_by_id_str(return_request.return_id.value)
    assert stored is not None
    assert stored.status == ReturnStatus.IMAGES_RECEIVED


@pytest.mark.asyncio
async def test_complete_image_upload_partial_keeps_awaiting_images(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    return_request = make_return_request(expected_image_count=3)
    await fake_return_repository.save(return_request)

    keys = make_pending_image_keys(return_request.return_id.value, 3)
    fake_image_storage.seed_uploaded(
        return_request.return_id.value, [k.value for k in keys]
    )

    use_case = CompleteImageUploadUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    result = await use_case.execute(
        return_id=return_request.return_id.value,
        image_keys=[keys[0].value, keys[1].value],
    )

    assert result.status == ReturnStatus.AWAITING_IMAGES
    assert result.image_count == 2
    assert result.all_images_received is False


@pytest.mark.asyncio
async def test_complete_image_upload_raises_when_return_missing(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    use_case = CompleteImageUploadUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    missing_id = ReturnId.generate().value
    keys = make_pending_image_keys(missing_id, 1)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(return_id=missing_id, image_keys=[keys[0].value])


@pytest.mark.asyncio
async def test_complete_image_upload_raises_for_key_not_uploaded(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    return_request = make_return_request(expected_image_count=3)
    await fake_return_repository.save(return_request)

    keys = make_pending_image_keys(return_request.return_id.value, 3)

    use_case = CompleteImageUploadUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    with pytest.raises(ImageUploadError):
        await use_case.execute(
            return_id=return_request.return_id.value,
            image_keys=[keys[0].value],
        )


@pytest.mark.asyncio
async def test_complete_image_upload_raises_for_key_belonging_to_other_return(
    fake_return_repository: FakeReturnRepository,
    fake_image_storage: FakeImageStorage,
) -> None:
    return_request = make_return_request(expected_image_count=3)
    await fake_return_repository.save(return_request)

    other_return_id = ReturnId.generate().value
    foreign_keys = make_pending_image_keys(other_return_id, 1)
    fake_image_storage.seed_uploaded(other_return_id, [foreign_keys[0].value])

    use_case = CompleteImageUploadUseCase(
        return_repository=fake_return_repository,
        image_storage=fake_image_storage,
    )

    with pytest.raises(ImageUploadError):
        await use_case.execute(
            return_id=return_request.return_id.value,
            image_keys=[foreign_keys[0].value],
        )
