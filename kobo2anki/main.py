import os
import logging

import click
from typing import List

from kobo2anki import model
from kobo2anki.kobo import reader as kobo_reader
from kobo2anki.dicts.oxforddictionaries import (
    client as dict_client,
)
from kobo2anki.dicts import errors as dict_errors

from kobo2anki.anki import anki

logger = logging.getLogger(__name__)


@click.command(context_settings={"ignore_unknown_options": False})
@click.argument(
    "kobo_path", type=click.Path(exists=True, file_okay=False),
)
@click.argument(
    "output_deck_path", type=click.Path(exists=False),
)
#@click.argument("dict_key", envvar='DICT_KEY')
#@click.argument("dict_app_id", envvar='DICT_APP_ID')
@click.option("--deck-name", default="Kobo words deck")
@click.option("--debug/--no-debug", default=False)
def main(kobo_path, output_deck_path, deck_name, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    dict_app_id = os.environ.get("DICT_APP_ID")
    if not dict_app_id:
        raise RuntimeError("Env variable 'DICT_APP_ID' isn't set or empty")
    dict_key = os.environ.get("DICT_KEY")
    if not dict_key:
        raise RuntimeError("Env variable 'DICT_KEY' isn't set or empty")

    words_definitions: List[model.WordDefinition] = []

    kobo_db = kobo_reader.KoboReader(kobo_path)
    dict_client_instance = dict_client.OxfordDictionaryClient(dict_app_id, dict_key)
    anki_deck = anki.AnkiDeck(deck_name)
    words_from_kobo = kobo_db.get_saved_words()

    # dedup words
    words_from_kobo = list(
        set(
            map(lambda x: x.lower(), words_from_kobo)
        )
    )
    logger.info("Read %d words from kobo", len(words_from_kobo))
    logger.debug("List of words from kobo: %s", words_from_kobo)

    for word_from_kobo in sorted(words_from_kobo):
        logger.debug("Trying to find defintion for word %s", word_from_kobo)
        try:
            word_definition = dict_client_instance.get_definition(word_from_kobo)
            words_definitions.append(word_definition)
            logger.debug("Found definition for word %s", word_from_kobo)
        except (dict_errors.WordTranslationNotFound):
            logger.warning(
                "Didn't find definition for word %s, will skip the word", word_from_kobo
            )
        except dict_errors.CantParseDictData as exc:
            logger.warning("Can't parse word %s. Error %s", word_from_kobo, exc)

        except dict_errors.NotAbleToGetWordTranlsation as exc:
            logger.error("Can't get word %s. Err: %s", word_from_kobo, exc)

    logger.debug("Going to generate anki deck for %d words", len(words_definitions))
    anki_deck.generate_and_save_deck(words_definitions, output_deck_path)
    logger.info(
        "Saved deck with %d words to %s",
        len(words_definitions),
        output_deck_path
    )


if __name__ == '__main__':
    main()
