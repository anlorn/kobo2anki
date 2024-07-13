"""
Stub of the dict for testing purposes
"""
from typing import Dict, Type
from logging import getLogger

from kobo2anki.model import WordDefinition
from kobo2anki.dicts import errors

logger = getLogger(__name__)


class FakeDictClient:
    """
    Stub of a dictionary client for testing purposes.
    """
    def __init__(self,
                 expected_definitions: Dict[str, WordDefinition],
                 expected_exceptions: Dict[str, Type[Exception]],
                 ):
        """
        Initialize the fake dictionary client with expected definitions and exceptions.
        If a word in expected_definitions, then expected definition will be returned.
        If a word is in expected_exceptions, it will raise the corresponding exception.
        If a word is not in the expected definitions, it will raise WorldTranslationNotFound error.
        """
        self._expected_definitions = expected_definitions
        self._expected_exceptions = expected_exceptions

    def get_definition(self, word: str) -> WordDefinition:
        if word in self._expected_definitions:
            logger.debug("Returning definition for word %s", word)
            return self._expected_definitions[word]
        if word in self._expected_exceptions:
            logger.debug("Raising exception for word %s", word)
            raise self._expected_exceptions[word]()
        logger.debug("Raising WordTranslationNotFound for word %s", word)
        raise errors.WordTranslationNotFound(word)

    def __repr__(self):
        return "FakeDictClient"