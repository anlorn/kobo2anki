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

    def test_generate_note_some_fields(
        self, mocker,
        genanki_note_mock,
        genanki_model_mock
    ):
        mocker.patch.object(model.genanki, "Model", genanki_model_mock)
        mocker.patch.object(model.genanki, "Note", genanki_note_mock)
        test_fields = {
            "picture": "some_image.png",
            "Word": "some_word",
            "part": "verb",
            "explanation_1": "expl1",
            "Synonym_2": "syn2",
            "explanation_2": "expl2",
            "example_2": "example2"
        }

        anki_model = model.AnkiModel()
        anki_model.generate_note(**test_fields)

        expected_model_calls = [
            mocker.call(
                model_id=anki_model.model_id,
                name='Learning English Model',
                fields=model.AnkiModel.fields,
                templates=[
                    {
                        "name": 'Learning English Model Template',
                        "qfmt": model.AnkiModel.front_template,
                        "afmt": model.AnkiModel.back_template

                    }
                ]

            )
        ]
        assert genanki_model_mock.call_args_list == expected_model_calls

        assert genanki_note_mock.call_args_list == [
            mocker.call(
                model=genanki_model_mock.return_value,
                fields=[
                    'some_word', 'verb', 'expl1',
                    '', '', 'expl2',
                    'syn2', 'example2', '', '', '', '', 'some_image.png'
                ]
            )
        ]

    def test_generate_note_unknown_fields(
        self, mocker,
        genanki_note_mock,
        genanki_model_mock
    ):
        mocker.patch.object(model.genanki, "Model", genanki_model_mock)
        mocker.patch.object(model.genanki, "Note", genanki_note_mock)
        test_fields = {
            "picture": "some_image.png",
            "word": "some_word",
            "part": "verb",
            "unknown_field_name": "some_value"
        }

        anki_model = model.AnkiModel()
        with pytest.raises(RuntimeError):
            anki_model.generate_note(**test_fields)
