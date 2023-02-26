import os
import pytest

from kobo2anki.kobo import db, model


@pytest.fixture
def test_db_path():
    return os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "data/test_db.sqlite"
    )


class TestKoboDB:

    def test_get_dict_words(self, test_db_path):

        # we know we saved these words in test DB
        expected_dict_words = [
            model.DictWord(text='bobbing.', dict_suffix='-en'),
            model.DictWord(text='goaded', dict_suffix='-en'),
            model.DictWord(text='lured', dict_suffix='-en'),
            model.DictWord(text='flatter', dict_suffix='-en'),
            model.DictWord(text='convalescent', dict_suffix='-en'),
        ]

        db_reader = db.KoboDB(test_db_path)
        dict_words = db_reader.get_dict_words()
        assert sorted(dict_words) == sorted(expected_dict_words)

    def test_get_highlights(self, test_db_path):

        # we know we saved these words in test DB
        expected_highlights = [
            model.HighLight(
                id='4bdc6cf1-2708-4ef6-b508-a4ef05d4775f',
                text='musings'
            ),
            model.HighLight(
                id='6148ee79-a3f8-4de2-b308-53b2b58e37a7',
                text=' ribald'
            ),
            model.HighLight(
                id='ccfd0458-99e0-4862-b87c-4db2d03809ff',
                text='frail'
            ),
            model.HighLight(
                id='eba8ddf4-c54a-44b5-ba16-aa1ade3dd0d9',
                text='harangues'
            ),
            model.HighLight(
                id='f3439f55-c651-48a3-8635-d556763d67cd',
                text='fret,'
            ),
        ]

        db_reader = db.KoboDB(test_db_path)
        highlights = db_reader.get_highlights()
        assert sorted(highlights) == sorted(expected_highlights)
