import hashlib
import logging
from typing import List

import genanki

from kobo2anki.anki import model
from kobo2anki.model import WordDefinition

logger = logging.getLogger(__name__)


class AnkiDeck:

    def __init__(self, deck_name: str):
        self._model = model.AnkiModel()
        self._name = deck_name

    def generate_and_save_deck(
            self,
            words_definitions: List[WordDefinition],
            filepath_for_new_deck: str,
    ):
        if not words_definitions:
            raise RuntimeError("List of words is empty")

        deck_id = self._generate_deck_id(words_definitions)
        deck = genanki.Deck(
            deck_id=deck_id,
            name=self._name,
        )

        for word_definition in words_definitions:
            self._add_word(deck, word_definition)
            logger.info(
                "Add word %s to deck %d",
                word_definition.word,
                deck_id
            )

        package = genanki.Package(deck)
        #  package.media_files = ['sound.ogg', 'sound.mp3', 'image.jpg']
        package.write_to_file(filepath_for_new_deck)

    def _generate_deck_id(self, words_definitions: List[WordDefinition]) -> int:
        """
        Generate Deck ID by using list of all sorted words + model id encoded in MD5
        and convereted to INT
        """
        all_words_str = "::".join(
            sorted(
                list(map(lambda definition: definition.word.lower(), words_definitions))
            )
        )
        key = f"{all_words_str}_{self._model.model_id}"
        deck_id = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return 123354654

    def _add_word(self, deck: genanki.Deck, word_definition: WordDefinition):

        for part_explanation in word_definition.explanations:
            args = {
                "word": word_definition.word,
                "part": part_explanation.part.value,
            }
            if not part_explanation.definitions:
                logger.warning(
                    "Definitions for word %s are empty, skipping word",
                    word_definition.word
                )
                continue
            for i, definition in enumerate(part_explanation.definitions[:2]):
                if not definition.definitions:
                    logger.warning(
                        "Definition %d for word %s is empty, skipping",
                        i + 1,
                        word_definition.word
                    )
                    continue
                args[f"explanation_{i+1}"] = ";".join(definition.definitions[:3])
                args[f"synonym_{i+1}"] = ";".join(definition.synonyms[:5])
                args[f"example_{i+1}"] = ";".join(definition.examples[:3])
            logger.debug(
                "Generated note for word %s(%s)",
                word_definition.word,
                part_explanation.part.value,
            )
            note = self._model.generate_note(**args)
            deck.add_note(note)
