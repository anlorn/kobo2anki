import json
import pytest
from unittest.mock import MagicMock, call, patch, mock_open

from kobo2anki.dicts import model
from kobo2anki.caching import get_cache_path
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
    return model.DictWord("word", "transcription", [])


@pytest.fixture
def parser_mock(mocker, dict_word_fixture):
    mock_parser = mocker.patch.object(client_module.parser, 'parse_data')
    mock_parser.return_value = dict_word_fixture
    return mock_parser


class TestOxfordDictionariesClient:

    test_app_id = "APP_ID"
    test_app_key = "APP_KEY"
    test_word = "example"

    def test_get_definition_success_no_cache(
        self,
        mocker,
        requests_fixture,
        dict_test_response,
        parser_mock,
        dict_word_fixture
    ):
        client = client_module.OxfordDictionaryClient(self.test_app_id, self.test_app_key)

        # simulate that cache file not found provide MagicMock when we try to save cache
        open_mock = mock_open()
        open_mock.side_effect = [
            FileNotFoundError("FileNotFoundError"),
            MagicMock(),
        ]
        with patch.object(client_module, "open", open_mock):
            response = client.get_definition(self.test_word)

        assert response == dict_word_fixture

        #  first ensure we tried to read cahce file and then saved it
        assert open_mock.call_args_list == [
            call(get_cache_path() + "/" + client_module.DICT_NAME + "/" + self.test_word + ".json", "r"),
            call(get_cache_path() + "/" + client_module.DICT_NAME + "/" + self.test_word + ".json", "w"),
        ]

        # then ensure we called dict with right credentials
        assert requests_fixture.call_args_list == [
            call(
                client_module.BASE_URL + client_module.LANGUAGE + "/" + self.test_word,
                headers={'app_id': self.test_app_id, "app_key": self.test_app_key}
            )
        ]

        # ensure we called parser with right data
        assert parser_mock.call_args_list == [call(dict_test_response)]

    def test_get_definition_success_cache_found(
        self,
        mocker,
        requests_fixture,
        dict_test_response,
        parser_mock,
        dict_word_fixture
    ):
        client = client_module.OxfordDictionaryClient(self.test_app_id, self.test_app_key)

        # simulate that cache file not found provide MagicMock when we try to save cache
        open_mock = mock_open(read_data=json.dumps(dict_test_response))

        with patch.object(client_module, "open", open_mock):
            response = client.get_definition(self.test_word)

        assert response == dict_word_fixture

        #  first ensure we tried to read cache file
        assert open_mock.call_args_list == [
            call(get_cache_path() + "/" + client_module.DICT_NAME + "/" + self.test_word + ".json", "r"),
        ]

        # then ensure we didn't call dict because we found value in the cache
        assert requests_fixture.call_count == 0

        # ensure we called parser with right data
        assert parser_mock.call_args_list == [call(dict_test_response)]
