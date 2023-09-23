import os
import hashlib
import tempfile
import logging
from typing import List, Optional

import genanki

from kobo2anki.anki import model
from kobo2anki.model import WordDefinition
from kobo2anki.image_searcher import ImageSearcher

logger = logging.getLogger(__name__)


class AnkiDeck:

    def __init__(self, deck_name: str, image_searcher: Optional[ImageSearcher] = None):
        self._name = deck_name
        self.tempdir = tempfile.mkdtemp()
        self._model = model.AnkiModel()
        self.image_searcher = image_searcher

    def generate_and_save_deck(
            self,
            words_definitions: List[WordDefinition],
            filepath_for_new_deck: str,
    ):
        if not words_definitions:
            raise RuntimeError("List of words is empty")

        os.chdir(self.tempdir)
        deck_id = self._generate_deck_id(words_definitions)
        deck = genanki.Deck(
            deck_id=deck_id,
            name=self._name,
        )
        media_files: List[str] = []
        for word_definition in words_definitions:
            self._add_word(deck, word_definition)
            logger.info(
                "Add word %s to deck %d",
                word_definition.word,
                deck_id
            )
            if word_definition.pronunciation:
                word_definition.pronunciation.save_audio_file_to(
                    os.path.join(self.tempdir, word_definition.pronunciation.get_filename())
                )
                media_files.append(word_definition.pronunciation.get_filename())
            if word_definition.image:
                word_definition.image.save_image_to(
                    os.path.join(self.tempdir, word_definition.image.get_filename())
                )
                media_files.append(word_definition.image.get_filename())

        package = genanki.Package(deck)
        #  package.media_files = ['sound.ogg', 'sound.mp3', 'image.jpg']
        package.media_files = media_files
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
            if word_definition.pronunciation is not None:
                args['pronunciation'] = f"[sound:{word_definition.pronunciation.get_filename()}]"
            if word_definition.image is not None:
                args['picture'] = f'[<img src="{word_definition.image.get_filename()}">]'

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
