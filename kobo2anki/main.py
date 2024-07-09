import os
import logging

import click
import random
from typing import List

from kobo2anki import model
from kobo2anki.kobo import reader as kobo_reader
from kobo2anki.dicts import of_client, freedict_client
from kobo2anki.dicts import errors as dict_errors
from kobo2anki.language_processor import LanguageProcessor
from kobo2anki.image_searcher import ImageSearcher
from kobo2anki.anki import anki

logger = logging.getLogger(__name__)


# TODO
# Add tests
# Restructure to make it simpler
@click.command(context_settings={"ignore_unknown_options": False})
@click.argument(
    "kobo_path", type=click.Path(exists=True, file_okay=False),
    help="Root folder for the kobo device",

)
@click.argument(
    "output_deck_path", type=click.Path(exists=False),
    help="Path and filename for created ANKI deck"
)
# TODO: Implement dict choosing
@click.option("--dict", type=click.Choice(['freedict', 'oxforddict', 'chatgpt']), default='freedict')
@click.option("--deck-name", default="Kobo words deck")
@click.option("--debug/--no-debug", default=False)

# TODO: Implement multiple decks creation
@click.option(
    "--limit", default=0,
    help="Maximum number of words deck can have. Multiplr decks would be created if more words are available."
    + "Amount of words not restriced if If value zet to zero or less"
)
# TODO: Implement it as caching, so user don't have to input it every time
@click.option(
    "--exclude_words_path", default='',
    help="Path to a file with a list words you want to exclude. One word per line."
    + "Can be useful if cleaning anki sqlite DB after every import is not desired."
)
def main(kobo_path, output_deck_path, deck_name, debug, limit, exclude_words_path):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    CLIENTS = []
    language_processor = LanguageProcessor()

    with open(exclude_words_path, 'r', encoding="utf-8") as fh:
        exclude_words = set(map(lambda x: x.strip(), fh.readlines()))
    for exclude_word in exclude_words:
        exclude_words.add(language_processor.lemmatize_word(exclude_word))

    dict_app_id = os.environ.get("DICT_APP_ID")
    dict_key = os.environ.get("DICT_KEY")
    if dict_app_id and dict_key:
        of_dict_client_instance = of_client.OxfordDictionaryClient(dict_app_id, dict_key)
        CLIENTS.append(of_dict_client_instance)
    else:
        logger.warning(
            "Env variables 'DICT_APP_ID' or 'DICT_KEY' are not defined, will not initialize oxford dictionoary"
        )

    gis_api_key = os.environ.get("GIS_API_KEY")
    search_cx = os.environ.get("SEARCH_CX")
    if gis_api_key and search_cx:
        image_searcher = ImageSearcher(gis_api_key, search_cx)
    else:
        logger.warning(
            "Env variables 'GIS_API_KEY' or 'SEARCH_CX' are not defined, will not add images to words"
        )
        image_searcher = None

    words_definitions: List[model.WordDefinition] = []
    kobo_db = kobo_reader.KoboReader(kobo_path)
    # TODO think how to make is extendable 
    freedict_client_instance = freedict_client.FreeDictionaryClient()
    CLIENTS.append(freedict_client_instance)
    anki_deck = anki.AnkiDeck(deck_name)
    words_from_kobo = kobo_db.get_saved_words()


    # dedup words
    words_from_kobo = list(
        set(
            map(lambda x: x.lower(), words_from_kobo)
        )
    )
    # exclude already processed words
    words_from_kobo = list(filter(lambda x: x not in exclude_words, words_from_kobo))

    random.shuffle(words_from_kobo)
    logger.info("Read %d words from kobo", len(words_from_kobo))
    logger.debug("List of words from kobo: %s", words_from_kobo)

    words_limit = limit if limit > 0 else len(words_from_kobo)
    logger.info("Limit number of words to %d", words_limit)


    # TODO: restructure to make it simpler
    for word_from_kobo in words_from_kobo[:words_limit]:
        word_definition = None
        word_from_kobo = language_processor.lemmatize_word(word_from_kobo)
        for dict_client in CLIENTS:
            logger.debug("Trying to find defintion for word %s, using %s", word_from_kobo, dict_client)
            try:
                word_definition = dict_client.get_definition(word_from_kobo)
                if image_searcher:
                    for explanation in word_definition.explanations:
                        if explanation.part == model.Parts.NOUN:
                            logger.info("Word %s has Noun part, will get image", word_definition.word)
                            word_definition.image = image_searcher.get_image_for_word(word_definition.word)
                            break
                else:
                    logger.debug("Will not try to get image for word %s", word_definition.word)

                words_definitions.append(word_definition)
                logger.info("Found definition for word %s using client %s", word_from_kobo, dict_client)
                break
            except dict_errors.WordTranslationNotFound:
                logger.warning(
                    "Didn't find definition for word %s, will skip the word", word_from_kobo
                )
            except dict_errors.CantParseDictData as exc:
                logger.warning("Can't parse word %s. Error %s", word_from_kobo, exc)

            except dict_errors.NotAbleToGetWordTranlsation as exc:
                logger.warning("Can't get word %s. Err: %s", word_from_kobo, exc)
        if word_definition is None:
            logger.error("Didn't find word defintion for word %s", word_from_kobo)

    logger.debug("Going to generate anki deck for %d words", len(words_definitions))
    anki_deck.generate_and_save_deck(words_definitions, output_deck_path)
    logger.info(
        "Saved deck with %d words to %s",
        len(words_definitions),
        output_deck_path
    )


if __name__ == '__main__':
    main()
