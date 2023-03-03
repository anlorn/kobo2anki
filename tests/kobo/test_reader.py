import os
import pytest
from unittest.mock import call
from pytest_mock import MockerFixture

from kobo2anki.kobo import reader, db, model


@pytest.fixture
def test_dict_words():
    return [
        model.DictWord(text=',bobbing.', dict_suffix='-en'),
        model.DictWord(text='goaded ', dict_suffix='-en'),
        model.DictWord(text='lured?', dict_suffix='-en'),
        model.DictWord(text='!flatter', dict_suffix='-en'),
        model.DictWord(text='convalescent,', dict_suffix='-en'),
    ]


@pytest.fixture
def test_highlights():
    return [
        model.HighLight(
            id='4bdc6cf1-2708-4ef6-b508-a4ef05d4775f',
            text='Some highlighted text'
        ),
        model.HighLight(
            id='6148ee79-a3f8-4de2-b308-53b2b58e37a7',
            text='er flatter t'
        ),
        model.HighLight(
            id='ccfd0458-99e0-4862-b87c-4db2d03809ff',
            text='ou frail. '
        ),
    ]


@pytest.fixture
def db_reader_mock(
        mocker: MockerFixture,
        test_dict_words,
        test_highlights,
):
    db_reader = mocker.MagicMock(spec=db.KoboDB)
    db_reader.return_value.get_dict_words.return_value = test_dict_words
    db_reader.return_value.get_highlights.return_value = test_highlights
    return db_reader


class TestKoboReader:
    def test_get_saved_words(
        self,
        mocker,
        db_reader_mock,
        test_dict_words,
        test_highlights,
    ):

        mocker.patch.object(reader.db, 'KoboDB', db_reader_mock)
        kobo_mount_path = os.path.abspath(__file__)
        kobo_reader = reader.KoboReader(kobo_mount_path)
        words = kobo_reader.get_saved_words()
        expected_words = [
            'bobbing', 'goaded', 'lured', 'flatter',
            'convalescent', 'flatter', 'frail'
        ]
        assert sorted(words) == sorted(expected_words)
        assert db_reader_mock.call_args_list == [
            call(os.path.join(kobo_mount_path, ".kobo/KoboReader.sqlite"))
        ]
