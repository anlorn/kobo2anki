import pytest
from typing import Optional
from pytest_mock import MockerFixture

from kobo2anki.caching import LocalFSCaching


@pytest.fixture
def cache_handler_factory(mocker: MockerFixture):

    def _factory(get_cache_response: Optional[bytes]):
        cache_handler = mocker.MagicMock(autospec=LocalFSCaching)
        cache_handler.return_value.get_cached_data.return_value = get_cache_response
        return cache_handler

    return _factory
