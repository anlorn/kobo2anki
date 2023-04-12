import json
import pytest

from kobo2anki import model
from kobo2anki.dicts.oxforddictionaries import client as client_module


@pytest.fixture
def dict_test_response():
    return {"id": 123}


@pytest.fixture
def requests_fixture(mocker, dict_test_response):
    # mock requests to return succesfull response
    get_mock = mocker.patch.object(client_module.requests, "get")
    get_mock.return_value.status_code = 200
    get_mock.return_value.json.return_value = dict_test_response
    return get_mock


@pytest.fixture
def dict_word_fixture():
    return model.WordDefinition("word", "transcription", [])


@pytest.fixture
def mock_word_pronunciation(mocker):
    return mocker.patch.object(client_module, "WordPronunciation")


@pytest.fixture
def parser_mock(mocker, dict_word_fixture):
    mock_parser = mocker.patch.object(client_module.parser, 'parse_data')
    mock_parser.return_value = dict_word_fixture
    return mock_parser


@pytest.fixture
def parser_get_audio_file_url_mock(mocker):
    mock_parser = mocker.patch.object(client_module.parser, 'get_audio_file_url')
    mock_parser.return_value = 'http://example.com'
    return mock_parser


class TestOxfordDictionariesClient:

    test_app_id = "APP_ID"
    test_app_key = "APP_KEY"
    test_word = "example"

    def test_get_definition_success_no_cache(
        self,
        mocker,
        cache_handler_factory,
        requests_fixture,
        dict_test_response,
        parser_mock,
        dict_word_fixture,
        parser_get_audio_file_url_mock,
        mock_word_pronunciation,
    ):
        # simulate that cache wasn't found
        cache_mock = cache_handler_factory(get_cache_response=None)
        mocker.patch.object(client_module, "LocalFSCaching", cache_mock)

        client = client_module.OxfordDictionaryClient(self.test_app_id, self.test_app_key)
        response = client.get_definition(self.test_word)

        assert response == dict_word_fixture
        mock_word_pronunciation.assert_called_once_with("http://example.com")

        # ensure cache handler was iniitilized
        assert cache_mock.call_count == 1

        # ensure we tried to read cache
        assert cache_mock.return_value.get_cached_data.call_args_list == [
            mocker.call(client_module.DICT_NAME, f"word_{self.test_word}.json")
        ]
        # ensure we tried to save cache
        assert cache_mock.return_value.save_data_to_cache.call_args_list == [
            mocker.call(
                client_module.DICT_NAME,
                f"word_{self.test_word}.json",
                json.dumps(dict_test_response).encode()
            )
        ]
        # then ensure we called dict with right credentials
        assert requests_fixture.call_args_list == [
            mocker.call(
                client_module.BASE_URL + client_module.LANGUAGE + "/" + self.test_word,
                headers={'app_id': self.test_app_id, "app_key": self.test_app_key}
            )
        ]

        # ensure we called parser with right data
        assert parser_mock.call_args_list == [mocker.call(dict_test_response)]

    def test_get_definition_success_cache_found(
        self,
        mocker,
        cache_handler_factory,
        requests_fixture,
        dict_test_response,
        parser_mock,
        dict_word_fixture,
        parser_get_audio_file_url_mock,
        mock_word_pronunciation,
    ):

        # simulate that we found cache file
        cache_mock = cache_handler_factory(
            get_cache_response=json.dumps(dict_test_response).encode()
        )
        mocker.patch.object(client_module, "LocalFSCaching", cache_mock)

        client = client_module.OxfordDictionaryClient(self.test_app_id, self.test_app_key)
        response = client.get_definition(self.test_word)

        assert response == dict_word_fixture

        # ensure we tried to read cache
        assert cache_mock.return_value.get_cached_data.call_args_list == [
            mocker.call(client_module.DICT_NAME, f"word_{self.test_word}.json")
        ]
        # ensure we didn't update cache
        assert cache_mock.return_value.save_data_to_cache.call_count == 0

        # then ensure we didn't call dict because we found value in the cache
        assert requests_fixture.call_count == 0

        # ensure we called parser with right data
        assert parser_mock.call_args_list == [mocker.call(dict_test_response)]
