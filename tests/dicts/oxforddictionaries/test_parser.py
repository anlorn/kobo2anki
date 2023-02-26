from kobo2anki.dicts import model
from kobo2anki.dicts.oxforddictionaries import parser
from tests.dicts.oxforddictionaries import data


def test_parsing():
    actual_word = parser.parse_data(data.response_data)
    excepted_word = model.DictWord(
        word="example",
        transcription="ɪɡˈzæmpəl",
        explanations=[
            model.PartExplanations(model.Parts.NOUN, definitions=[
                model.Definition(
                    definitions=[
                        'a thing characteristic of its kind or illustrating a general rule'
                    ],
                    synonyms=[
                        'specimen', 'sample', 'exemplar', 'exemplification', 'instance',
                        'case', 'representative case', 'typical case', 'case in point',
                        'illustration'
                    ],
                    examples=[
                        "it's a good example of how European action can produce results",
                        "some of these carpets are among the finest examples of the period",
                    ]
                ),
                model.Definition(
                    definitions=[
                        'a person or thing regarded in terms of their fitness to be imitated or the likelihood of their being imitated'
                    ],
                    synonyms=[
                        'precedent', 'lead', 'guide', 'model', 'pattern', 'blueprint',
                        'template', 'paradigm', 'exemplar', 'ideal', 'standard'],
                    examples=[
                        'it is vitally important that parents should set an example',
                        "she followed her brother's example and deserted her family",
                    ]
                )
            ]),
            model.PartExplanations(model.Parts.VERB, definitions=[
                model.Definition(
                    definitions=[
                        'be illustrated or exemplified'
                    ],
                    synonyms=[],
                    examples=[
                        'the extent of Allied naval support is exampled by the navigational specialists provided'
                    ]
                )
            ]),
        ]
    )

    assert actual_word.word == excepted_word.word

    assert actual_word == excepted_word
