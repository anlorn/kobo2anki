from typing import Dict

import json
import logging
import requests

from kobo2anki import model
from kobo2anki.dicts import errors
from kobo2anki.pronunciation import WordPronunciation
from kobo2anki.dicts.freedict.pronunciation_guesser import PronunciationURLGuesser


logger = logging.getLogger(__name__)


class FreeDictionaryClient:

    def __init__(self):
        self.pronunciation_url_guesser = PronunciationURLGuesser()

    def get_definition(self, word: str) -> model.WordDefinition:
        """
        Experimental, asked chatGPT to write code for API
        """
        logger.info("Getting defintion for word %s, using 'freedict'", word)
        base_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        try:
            logger.debug(
                "Will use url %s to get word %s definition", base_url + word, word)
            response = requests.get(base_url + word, timeout=10)
            logger.debug("Got response with code %d", response.status_code)
            if response.status_code == 404:
                raise errors.WordTranslationNotFound(word)

            if response.status_code != 200:
                raise errors.NotAbleToGetWordTranlsation(
                    word,
                    f"Got status code {response.status_code}"
                )
            try:
                data = response.json()
                logger.debug("Parsed response: %s", data)
            except json.JSONDecodeError as exc:
                raise errors.CantParseDictData(f"Response JSON can't be parsed. Err: {exc}")
        except requests.RequestException as exc:  # the most general error
            raise errors.NotAbleToGetWordTranlsation(word, exc) from exc
        explanations: Dict = {}
        for meaning in data[0]["meanings"]:
            part = model.Parts(meaning["partOfSpeech"])
            logger.debug("Found defintion for part %s", part)

            if part not in explanations:
                explanations[part] = []

            definitions_list = []
            for def_data in meaning["definitions"]:
                definitions = [def_data.get("definition", "")]
                synonyms = def_data.get("synonyms", [])
                examples = [def_data.get("example")] if def_data.get("example") else []

                definition = model.Definition(definitions=definitions, synonyms=synonyms, examples=examples)
                logger.debug(
                    "Added defintion '%s' with synonyms '%s' and examples '%s'",
                    definition, synonyms, examples
                )
                definitions_list.append(definition)

            explanations[part].extend(definitions_list)

        part_explanations = [model.PartExplanations(part=k, definitions=v) for k, v in explanations.items()]
        transcription = data[0].get("phonetic", None)
        pronunciation_url = data[0].get("phonetics")[0].get("audio") if data[0].get("phonetics") else None
        if pronunciation_url:
            logger.debug("Found pronunciation, url - %s", pronunciation_url)
            pronunciation = WordPronunciation(pronunciation_url)
        else:
            logger.info("Word has no pronunciation, will true to guess it")
            url = self.pronunciation_url_guesser.get_url(word)
            if url:
                logger.info("Was able to guess URL for for word '%s'", word)
                pronunciation = WordPronunciation(url)
            else:
                logger.info("Wasn't able to guess URL")
                pronunciation = None
        return model.WordDefinition(
            word=word, transcription=transcription,
            explanations=part_explanations, pronunciation=pronunciation
        )

    def __repr__(self):
        return "OxfordDictionaryClient"
