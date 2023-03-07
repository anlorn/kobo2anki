import os
import pytest
import requests
import tempfile


from kobo2anki import pronunciation, errors


@pytest.fixture
def requests_mock(mocker):
    def inner(method: str, status_code: int, response: bytes):
        mock = mocker.MagicMock(autospec=requests)
        method_func = getattr(mock, method)
        method_func.return_value.content = response
        method_func.return_value.status_code = status_code
        return mock

    return inner


class TestWordPronunciation:
    test_url = "https://audio.example.com/mp3/test__us_1.mp3"
    test_filename = "example.mp3"
    test_response = b"123"

    def test_save_audio_file_to_success_no_cache(
        self, mocker, requests_mock, cache_handler_factory,
    ):
        get_mock = requests_mock("get", 200, self.test_response)
        mocker.patch.object(
            pronunciation,
            "requests",
            get_mock
        )

        cache_mock = cache_handler_factory(None)
        mocker.patch.object(pronunciation, "LocalFSCaching", cache_mock)

        wp = pronunciation.WordPronunciation(self.test_url)
        with tempfile.TemporaryDirectory() as tmpdirname:
            test_fullpath = os.path.join(tmpdirname, self.test_filename)
            wp.save_audio_file_to(test_fullpath)
            with open(test_fullpath, 'rb') as fh:
                assert fh.read() == self.test_response
        # verify we called right url
        assert get_mock.get.call_args_list == [mocker.call(self.test_url)]

        # verify we tried to get cache
        assert cache_mock.return_value.get_cached_data.call_args_list == [
            mocker.call(
                pronunciation.WordPronunciation.cache_entity,
                self.test_url.split("/")[-1]
            )
        ]

        # verify we saved cache
        assert cache_mock.return_value.save_data_to_cache.call_args_list == [
            mocker.call(
                pronunciation.WordPronunciation.cache_entity,
                self.test_url.split("/")[-1],
                self.test_response
            )
        ]

    def _test_save_audio_file_to_error_response(
        self, mocker, requests_mock, cache_handler_factory,
    ):
        get_mock = requests_mock("get", 500, b"")
        mocker.patch.object(
            pronunciation,
            "requests",
            get_mock
        )

        wp = pronunciation.WordPronunciation(self.test_url)
        with tempfile.TemporaryDirectory() as tmpdirname:
            test_fullpath = os.path.join(tmpdirname, self.test_filename)
            with pytest.raises(errors.GettingPronunciationError):
                wp.save_audio_file_to(test_fullpath)


