import pytest
import tempfile
from click.testing import CliRunner
from kobo2anki.main import main, cli
from tests.stubs.dict import FakeDictClient
from tests.stubs.kobo import FakeKoboReader
from kobo2anki.anki.anki import AnkiDeck
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
    limit = 0
    image_searcher = None
    with tempfile.TemporaryDirectory() as output_deck_path:
        with pytest.raises(RuntimeError):
            main(
                dict_client,
                kobo_db,
                anki_deck_generator,
                language_processor,
                output_deck_path,
                limit,
                image_searcher,
                [],
            )
