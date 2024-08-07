import os
import tempfile
from typing import Callable
from click.testing import CliRunner

import pytest

from kobo2anki.main import main, cli
from tests.stubs.dict import FakeDictClient
from tests.stubs.kobo import FakeKoboReader
from kobo2anki.anki.anki import AnkiDeck
from kobo2anki.model import WordDefinition
from kobo2anki.language_processor import LanguageProcessor


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0


def test_main_no_words_definitions():
    """
    We don't generate deck and raise a runtime error(for noe) when no words definitions are found.
    """
    dict_client = FakeDictClient(
        expected_definitions={},
        expected_exceptions={},
    )
    kobo_db = FakeKoboReader(['test'])
    anki_deck_generator = AnkiDeck('Test Deck', None)
    language_processor = LanguageProcessor()
    words_per_deck = 0
    image_searcher = None
    with tempfile.TemporaryDirectory() as output_deck_path:
        with pytest.raises(RuntimeError):
            main(
                dict_client,
                kobo_db,
                anki_deck_generator,
                language_processor,
                output_deck_path,
                words_per_deck,
                image_searcher,
                set([]),
            )


def test_main_successful_deck_generation(
        word_definition_factory: Callable[[str], WordDefinition],
):
    """
    Simplest case where we successfully generate a deck with one word definition.
    just one word, no limit or image searcher.
    """

    test_definition = word_definition_factory("test")
    dict_client = FakeDictClient(
        expected_definitions={
            "test": test_definition

        },
        expected_exceptions={},
    )
    kobo_db = FakeKoboReader(['test'])
    anki_deck_class = AnkiDeck
    language_processor = LanguageProcessor()
    words_per_deck = 0
    image_searcher = None
    with tempfile.TemporaryDirectory() as output_deck_path:
        added_words = main(
            dict_client,
            kobo_db,
            anki_deck_class,
            language_processor,
            output_deck_path,
            words_per_deck,
            image_searcher,
            set([]),
        )
        # here we just test that not empty file was created
        expected_deck_file_path = os.path.join(output_deck_path, f"{0:04}.apkg")
        assert os.path.isfile(expected_deck_file_path)
        assert os.path.getsize(expected_deck_file_path) > 0

        assert added_words == [test_definition]


def test_main_successful_deck_generation_with_exclusion(
        word_definition_factory: Callable[[str], WordDefinition],
):
    """
    Test that exclusion list being used to prevent words from being included in the deck.
    """
    test_definition = word_definition_factory("test")
    example_definition = word_definition_factory("example")
    dict_client = FakeDictClient(
        expected_definitions={
            "test": test_definition,
            "example": example_definition,

        },
        expected_exceptions={},
    )
    kobo_db = FakeKoboReader(['test', 'example'])
    anki_deck_class = AnkiDeck
    language_processor = LanguageProcessor()
    words_per_deck = 0
    image_searcher = None
    with tempfile.TemporaryDirectory() as output_deck_path:
        added_words = main(
            dict_client,
            kobo_db,
            anki_deck_class,
            language_processor,
            output_deck_path,
            words_per_deck,
            image_searcher,
            set(["example"]),
        )
        # here we just test that not empty file was created
        expected_deck_file_path = os.path.join(output_deck_path, f"{0:04}.apkg")
        assert os.path.isfile(expected_deck_file_path)
        assert os.path.getsize(expected_deck_file_path) > 0

        assert added_words == [test_definition]


def test_main_successful_deck_generation_multiple_decks(
        word_definition_factory: Callable[[str], WordDefinition],
):
    """
    We test case when we have more words than max number of words per on deck.
    So, multiple decks should be created.
    """
    test_definition = word_definition_factory("test")
    example_definition = word_definition_factory("example")
    dict_client = FakeDictClient(
        expected_definitions={
            "test": test_definition,
            "example": example_definition,

        },
        expected_exceptions={},
    )
    kobo_db = FakeKoboReader(['test', 'example'])
    anki_deck_class = AnkiDeck
    language_processor = LanguageProcessor()
    words_per_deck = 1
    image_searcher = None
    with tempfile.TemporaryDirectory() as output_deck_path:
        added_words = main(
            dict_client,
            kobo_db,
            anki_deck_class,
            language_processor,
            output_deck_path,
            words_per_deck,
            image_searcher,
            set([]),
        )
        # here we just test that not empty file was created
        expected_first_deck_file_path = os.path.join(output_deck_path, f"{0:04}.apkg")
        expected_second_deck_file_path = os.path.join(output_deck_path, f"{1:04}.apkg")
        assert os.path.isfile(expected_first_deck_file_path)
        assert os.path.getsize(expected_first_deck_file_path) > 0

        assert os.path.isfile(expected_second_deck_file_path)
        assert os.path.getsize(expected_second_deck_file_path) > 0

        assert sorted(added_words) == sorted([test_definition, example_definition])
