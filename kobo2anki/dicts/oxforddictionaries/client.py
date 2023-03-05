import json
import logging
import requests
from urllib.parse import urljoin
from typing import Dict, Optional


from kobo2anki.caching import LocalFSCaching
from kobo2anki.dicts.oxforddictionaries import parser
from kobo2anki.dicts import errors
from kobo2anki import model

logger = logging.getLogger(__name__)

BASE_URL = "https://od-api.oxforddictionaries.com:443/api/v2/entries/"
LANGUAGE = "en-us"
DICT_NAME = "oxforddictionaries"


class OxfordDictionaryClient:

    def __init__(self, app_id: str, app_key: str):
        self._app_id = app_id
        self._app_key = app_key
        self._cache_handler = LocalFSCaching()

    def get_definition(self, word: str) -> model.WordDefinition:
        json_response = self._get_raw_response(word)
        definition = self._parse_json_definition(word, json_response)

        return definition

    def _parse_json_definition(self, word: str, raw_response: Dict) -> model.WordDefinition:
        return parser.parse_data(raw_response)

    def _get_raw_response(self, word: str) -> Dict:
        response_json = self._get_cached_json(word)
        if response_json is None:
            response_json = self._get_word_from_dictionary(word)
            self._save_response_to_cache(word, response_json)
        return response_json

    def _get_word_cache_key(self, word: str) -> str:
        cache_key = f"word_{word}.json"
        return cache_key

    def _get_cached_json(self, word: str) -> Optional[Dict]:
        result = None  # type: Optional[Dict]
        cached_data = self._cache_handler.get_cached_data(
            DICT_NAME,
            self._get_word_cache_key(word)
        )
        if cached_data is None:
            logger.debug("We don't have cache from word '%s'", word)
        else:
            try:
                result = json.loads(cached_data)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Can't parse cache json for word '%s'. Err: %s",
                    word,
                    exc
                )
        return result

    def _save_response_to_cache(self, word: str, response_json: Dict):
        self._cache_handler.save_data_to_cache(
            DICT_NAME,
            self._get_word_cache_key(word),
            json.dumps(response_json).encode()
        )
        logger.debug(
            "Saved cache for word %s", word
        )

    def _get_word_from_dictionary(self, word: str) -> Dict:
        url = urljoin(
            BASE_URL,
            LANGUAGE + "/" + word.lower()
        )
        try:
            logger.debug("Will use '%s' for word %s", url, word)
            response = requests.get(
                url,
                headers={"app_id": self._app_id, "app_key": self._app_key}
            )
            if response.status_code == 404:
                raise errors.WordTranslationNotFound(word)
            if response.status_code != 200:
                raise errors.NotAbleToGetWordTranlsation(
                    word,
                    f"Got status code {response.status_code}"
                )
            response_json = response.json()
            logger.info("Got translation for word %s", word)
            logger.debug("Response for word %s is '%s'", word, response_json)
            return response_json
        except requests.RequestException as exc:
            raise errors.NotAbleToGetWordTranlsation(word, exc) from exc
