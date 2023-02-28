import shutil
import pytest
import appdirs
import tempfile
from pytest_mock import MockerFixture

from kobo2anki import caching


@pytest.fixture
def appdirs_mock(mocker: MockerFixture):
    mock = mocker.MagicMock(spec=appdirs)
    temp_folder = tempfile.mkdtemp()
    mock.user_cache_dir.return_value = temp_folder
    yield mock
    shutil.rmtree(temp_folder)


class TestLocalFSCaching:

    test_key = "pytest"
    test_entity = "somefile.bin"
    test_data = b"some_test_data"

    def test_get_cached_data_no_file(self, mocker, appdirs_mock):
        mocker.patch.object(caching, 'appdirs', appdirs_mock)
        cache_handler = caching.LocalFSCaching()
        cached_data = cache_handler.get_cached_data(
            self.test_key,
            self.test_entity
        )
        assert cached_data is None

    def test_save_and_get_cache(
        self,
        mocker,
        appdirs_mock
    ):
        mocker.patch.object(caching, 'appdirs', appdirs_mock)
        cache_handler = caching.LocalFSCaching()
        cache_handler.save_data_to_cache(
            self.test_key,
            self.test_entity,
            self.test_data
        )

        cached_data = cache_handler.get_cached_data(
            self.test_key,
            self.test_entity
        )
        assert cached_data == self.test_data

    def test_overwrite_cache(
        self,
        mocker,
        appdirs_mock
    ):
        mocker.patch.object(caching, 'appdirs', appdirs_mock)
        cache_handler = caching.LocalFSCaching()

        # save cache first time
        cache_handler.save_data_to_cache(
            self.test_key,
            self.test_entity,
            b"some_other_data-" + self.test_data
        )

        # now save cache second time
        cache_handler.save_data_to_cache(
            self.test_key,
            self.test_entity,
            self.test_data
        )

        # ensure we read cachhe we saved second time
        cached_data = cache_handler.get_cached_data(
            self.test_key,
            self.test_entity
        )
        assert cached_data == self.test_data
