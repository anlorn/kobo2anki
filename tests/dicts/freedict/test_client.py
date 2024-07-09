import pytest
import requests
from unittest.mock import MagicMock
from kobo2anki.dicts.freedict import client
from kobo2anki.model import Parts, Definition, PartExplanations, WordDefinition


@pytest.fixture
def mock_word_pronunciation(mocker):
    return mocker.patch("kobo2anki.dicts.freedict.client.WordPronunciation")


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("kobo2anki.dicts.freedict.client.requests.get")


class TestFreeDictinaryClient:

    test_app_id = "APP_ID"
    test_app_key = "APP_KEY"
    test_word = "example"

    def test_get_definition(self, mock_requests_get, mock_word_pronunciation):

        mock_data = [
            {
                "word": "example",
                "phonetic": "/ɪɡˈzæmpəl/",
                "phonetics": [
                    {
                        "text": "/ɪɡˈzæmpəl/",
                        "audio": "https://lex-audio.useremarkable.com/mp3/example_us_1.mp3",
                    }

                ],
                "meanings": [
                    {
                        "partOfSpeech": "noun",
                        "definitions": [
                            {
                                "definition": "A representative form or pattern.",
                                "synonyms": ["model", "pattern"],
                                "example": "I tried to set an example."
                            }
                        ]
                    }
                ]
            }
        ]

        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data

        mock_requests_get.return_value = mock_response

        word = "example"
        result = client.FreeDictionaryClient().get_definition(word)

        expected_result = WordDefinition(
            word="example",
            transcription="/ɪɡˈzæmpəl/",
            explanations=[
                PartExplanations(
                    part=Parts.NOUN,
                    definitions=[
                        Definition(
                            definitions=["A representative form or pattern."],
                            synonyms=["model", "pattern"],
                            examples=["I tried to set an example."]
                        )
                    ]
                )
            ],
            pronunciation=mock_word_pronunciation.return_value
        )

        assert result == expected_result
        mock_word_pronunciation.assert_called_once_with(
            'https://lex-audio.useremarkable.com/mp3/example_us_1.mp3'
        )

    def test_get_word_definition_multiple_meanings(self, mock_requests_get, mock_word_pronunciation):
        mock_data = [
            {
                "word": "coax",
                "phonetic": "/kəʊks/",
                "phonetics": [
                    {
                        "text": "/kəʊks/",
                        "audio": "https://lex-audio.useremarkable.com/mp3/coax_gb_1.mp3"
                    }
                ],
                "meanings": [
                    {
                        "partOfSpeech": "verb",
                        "definitions": [
                            {
                                "definition": "Persuade (someone) gradually or by flattery to do something.",
                                "synonyms": ["persuade", "cajole"],
                                "example": "The trainees were coaxed into doing boring jobs."
                            },
                            {
                                "definition": "Some other definition",
                                "synonyms": ["some_synonum"],
                                "example": "Some example"
                            }

                        ]
                    },
                    {
                        "partOfSpeech": "adjective",
                        "definitions": [
                            {
                                "definition": "Pretended; feigned.",
                                "example": "He had a coax smile."
                            }
                        ]
                    }
                ]
            }
        ]

        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data

        mock_requests_get.return_value = mock_response

        word = "coax"
        result = client.FreeDictionaryClient().get_definition(word)

        expected_result = WordDefinition(
            word="coax",
            transcription="/kəʊks/",
            pronunciation=mock_word_pronunciation.return_value,
            explanations=[
                PartExplanations(
                    part=Parts.VERB,
                    definitions=[
                        Definition(
                            definitions=["Persuade (someone) gradually or by flattery to do something."],
                            synonyms=["persuade", "cajole"],
                            examples=["The trainees were coaxed into doing boring jobs."]
                        ),
                        Definition(
                            definitions=["Some other definition"],
                            synonyms=["some_synonum"],
                            examples=["Some example"]
                        )
                    ]
                ),
                PartExplanations(
                    part=Parts.ADJECTIVE,
                    definitions=[
                        Definition(
                            definitions=["Pretended; feigned."],
                            examples=["He had a coax smile."],
                            synonyms=[],
                        )
                    ]
                )
            ]
        )

        assert result == expected_result
        mock_word_pronunciation.assert_called_once_with(
            'https://lex-audio.useremarkable.com/mp3/coax_gb_1.mp3'
        )
