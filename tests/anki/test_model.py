import pytest
import genanki
from pytest_mock import MockerFixture

from kobo2anki.anki import model

@pytest.fixture
def genanki_note_mock(mocker: MockerFixture):
    return mocker.MagicMock(autospec=genanki.Note)


@pytest.fixture
def genanki_model_mock(mocker: MockerFixture):
    return mocker.MagicMock(autospec=genanki.Model)


class TestAnkiModel:

    test_fields = {
        "Synonym_1": "syn1",
        "word": "some_word",
        "part": "verb",
        "Explanation_1": "expl1",
        "Synonym_2": "syn2",
        "explanation_2": "expl2",
        "example_1": "example1"
    }

    def test_generate_note(
        self, mocker,
        genanki_note_mock,
        genanki_model_mock
    ):
        mocker.patch.object(model.genanki, "Model", genanki_model_mock)
        mocker.patch.object(model.genanki, "Note", genanki_note_mock)
        anki_model = model.AnkiModel()
        anki_model.generate_note(**self.test_fields)


        asser genanki_model_mock.call_args_list == [
            call()
        ]
