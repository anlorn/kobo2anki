import pytest
import genanki

from unittest.mock import ANY, MagicMock
from pytest_mock import MockerFixture

from kobo2anki import model as root_model
from kobo2anki.anki import model, anki


@pytest.fixture(scope="class")
def genaki_notes_mocks():
    return [
        MagicMock(autospec=genanki.Note),
        MagicMock(autospec=genanki.Note),
        MagicMock(autospec=genanki.Note),
        MagicMock(autospec=genanki.Note),
        MagicMock(autospec=genanki.Note),
        MagicMock(autospec=genanki.Note),
    ]


@pytest.fixture
def anki_model_mock(mocker, genaki_notes_mocks):
    mock = mocker.MagicMock(autospec=model.AnkiModel)
    mock.return_value.generate_note.side_effect = genaki_notes_mocks
    return mock


@pytest.fixture
def genanki_deck_mock(mocker: MockerFixture):
    return mocker.MagicMock(autospec=genanki.Deck)


@pytest.fixture
def word_definition_generator():
    def inner(prefix: str):
        return root_model.WordDefinition(
            word=f"{prefix}word", transcription=f"{prefix}transcription",
            explanations=[
                root_model.PartExplanations(
                    part=root_model.Parts.NOUN,
                    definitions=[
                        root_model.Definition(
                            definitions=[f"{prefix}def11", f"{prefix}def12", f"{prefix}def13", f"{prefix}def14"],
                            synonyms=[f"{prefix}syn11", f"{prefix}syn11"],
                            examples=[f"{prefix}ex11"],
                        ),
                        root_model.Definition(
                            definitions=[f"{prefix}def21", f"{prefix}def22", f"{prefix}def23", f"{prefix}def24"],
                            synonyms=[f"{prefix}syn21", f"{prefix}syn21"],
                            examples=[f"{prefix}ex21"],
                        )
                    ]
                ),
                root_model.PartExplanations(
                    part=root_model.Parts.VERB,
                    definitions=[
                        root_model.Definition(
                            definitions=[f"{prefix}second_def11"],
                            synonyms=[],
                            examples=[],
                        ),

                    ]
                )
            ],
        )
    return inner


@pytest.fixture
def genanki_package_mock(mocker: MockerFixture):
    return mocker.MagicMock(autospec=genanki.Package)


class TestAnkiDeck:

    deck_name = "test_deck"
    save_path = "/some/path/to_save_deck"

    def test_generate_and_save_deck(
        self,
        mocker,
        anki_model_mock,
        genanki_deck_mock,
        genanki_package_mock,
        genaki_notes_mocks,
        word_definition_generator
    ):
        mocker.patch.object(anki.model, "AnkiModel", anki_model_mock)
        mocker.patch.object(anki.genanki, "Deck", genanki_deck_mock)
        mocker.patch.object(anki.genanki, "Package", genanki_package_mock)

        words = [word_definition_generator(""), word_definition_generator("second-")]

        anki_deck = anki.AnkiDeck(deck_name=self.deck_name)
        anki_deck.generate_and_save_deck(words, self.save_path)

        assert genanki_package_mock.call_count == 1
        assert genanki_package_mock.return_value.write_to_file.call_args_list == [
            mocker.call(self.save_path)
        ]

        assert genanki_deck_mock.call_args_list == [
            mocker.call(deck_id=ANY, name=self.deck_name)
        ]

        # we expect add_note called for every word part(each word has 2)
        expected_add_note_calls = []
        for i in range(len(words) * 2):
            expected_add_note_calls.append(mocker.call(genaki_notes_mocks[i]))
        assert genanki_deck_mock.return_value.add_note.call_args_list == expected_add_note_calls

        assert anki_model_mock.return_value.generate_note.call_args_list == [
            mocker.call(
                word='word', part='noun', explanation_1='def11;def12;def13',
                synonym_1='syn11;syn11', example_1='ex11',
                explanation_2='def21;def22;def23', synonym_2='syn21;syn21', example_2='ex21'
            ),
            mocker.call(
                word='word', part='verb',
                explanation_1='second_def11',
                synonym_1='', example_1=''
            ),
            mocker.call(
                word='second-word', part='noun',
                explanation_1='second-def11;second-def12;second-def13',
                synonym_1='second-syn11;second-syn11', example_1='second-ex11',
                explanation_2='second-def21;second-def22;second-def23',
                synonym_2='second-syn21;second-syn21', example_2='second-ex21'
            ),
            mocker.call(
                word='second-word', part='verb',
                explanation_1='second-second_def11',
                synonym_1='', example_1='',
            )
        ]
