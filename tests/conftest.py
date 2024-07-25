import pytest
from typing import Optional
from pytest_mock import MockerFixture

from kobo2anki.caching import LocalFSCaching
from kobo2anki import model
from kobo2anki.model import WordDefinition


@pytest.fixture
def cache_handler_factory(mocker: MockerFixture):

    def _factory(get_cache_response: Optional[bytes]):
        cache_handler = mocker.MagicMock(autospec=LocalFSCaching)
        cache_handler.return_value.get_cached_data.return_value = get_cache_response
        return cache_handler

    return _factory


@pytest.fixture
def word_definition_factory():
    """
    Generates a fake WordDefinition for a word.
    """
    def _factory(word: str):
        word_definition: WordDefinition = model.WordDefinition(
            word=word,
            transcription="test",
            explanations=[
                model.PartExplanations(
                    part=model.Parts.NOUN,
                    definitions=[
                        model.Definition(
                            definitions=[f"{word} definition 1"],
                            synonyms=[
                                f"{word}_synonym_1",
                                f"{word}_synonym_3",
                                f"{word}_synonym_3",
                            ],
                            examples=[
                                f"{word} usage example 1",
                                f"{word} usage example 2",
                                f"{word} usage example 3",
                            ],
                        )
                    ]
                )
            ],
        )
        return word_definition

    return _factory