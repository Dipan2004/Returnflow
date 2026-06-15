from __future__ import annotations

import os

os.environ.setdefault("DEMO_MODE", "false")

import pytest

from tests.fakes.fake_image_storage import FakeImageStorage
from tests.fakes.fake_return_repository import FakeReturnRepository


@pytest.fixture
def fake_return_repository() -> FakeReturnRepository:
    return FakeReturnRepository()


@pytest.fixture
def fake_image_storage() -> FakeImageStorage:
    return FakeImageStorage()
