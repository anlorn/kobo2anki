import logging
from typing import List

from kobo2anki import model
from kobo2anki.kobo import reader as kobo_reader
from kobo2anki.dicts.oxforddictionaries import (
    client as dict_client,
)
from kobo2anki.dicts import errors as dict_errors

from kobo2anki.anki import anki

logger = logging.getLogger(__name__)


def main():
    mount_path = ""
    dict_app_id = ""
    dick_key = ""
    anki_deck_name = ""
    anki_deck_saving_path = ""

    words_definitions: List[model.WordDefinition] = []

    kobo_db = kobo_reader.KoboReader(mount_path)
    dict_client_instance = dict_client.OxfordDictionaryClient(dict_app_id, dick_key)
    anki_deck = anki.AnkiDeck(anki_deck_name)
    words_from_kobo = kobo_db.get_saved_words()

    for word_from_kobo in words_from_kobo:
        try:
            word_definition = dict_client_instance.get_definition(word_from_kobo)
            words_definitions.append(word_definition)
        except (dict_errors.WordTranslationNotFound):
            logger.warning(
                "Didn't find definition for word %s, will skip the word", word_from_kobo
            )

    anki_deck.generate_and_save_deck(words_definitions, anki_deck_saving_path)
    logger.info(
        "Saved deck with %d words to %s",
        len(words_definitions),
        anki_deck_saving_path
    )
