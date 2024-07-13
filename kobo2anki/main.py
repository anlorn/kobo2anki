import os
import sys
import random
import logging
from typing import List, Set, Optional

import click

from kobo2anki import model
from kobo2anki.kobo import reader as kobo_reader
from kobo2anki.kobo import KoboDBReaderProtocol
from kobo2anki.dicts import CLIENTS, DictClient
from kobo2anki.dicts import errors as dict_errors
from kobo2anki.language_processor import LanguageProcessor
from kobo2anki.image_searcher import ImageSearcher
from kobo2anki.anki import anki

logger = logging.getLogger(__name__)


# TODO
# Add tests
# Restructure to make it simpler
@click.command(help="""
KOBO_PATH - is a path to root folder for connected Kobo e-reader.
OUTPUT_DECK_PATH - is a path(including filename) for created anki deck.
""", context_settings={"ignore_unknown_options": False})
@click.argument(
    "kobo_path", type=click.Path(exists=True, file_okay=False),
)
@click.argument(
    "output_deck_path", type=click.Path(exists=False),
)
# TODO: Implement dict choosing
@click.option("--dict-client", show_default=True,
              type=click.Choice(['freedict', 'oxforddict']), default='freedict',
              help="Choose dictionary for translation. Currently supported: freedict, oxforddict"
              )
@click.option("--deck-name", show_default=True,
              default="Kobo words deck"
              )
@click.option("--debug/--no-debug", default=False, show_default=False)
# TODO: Implement multiple decks creation
@click.option(
    "--limit", default=0, show_default=True,
    help="Maximum number of words deck can have. Multiple decks would be created if more words"
         + "are available. Amount of words not restricted if If value zet to zero or less"
)
# TODO: Implement it as caching, so user don't have to input it every time
@click.option(
    "--exclude_words_path", default='', show_default=False,
    help="Path to a file with a list words you want to exclude. One word per line."
         + "Can be useful if cleaning anki sqlite DB after every import is not desired."
)
def cli(kobo_path, output_deck_path, dict_client, deck_name, debug, limit, exclude_words_path):  # pylint: disable=too-many-arguments, too-many-locals
    """
    Main enter function for command line interface
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Select correct dict client class
    try:
        dict_client_class = CLIENTS[dict]
    except KeyError:
        logger.error(
            "Unsupported dictionary %s, supported dictionaries: %s",
            dict,
            list(CLIENTS.keys())
        )
        sys.exit(1)
    logger.debug("Using dict client: %s", type(dict_client_class))

    # initialize dict client class
    # TODO: Rework
    if dict_client_class == CLIENTS["oxforddict"]:
        dict_app_id = os.environ.get("DICT_APP_ID")
        dict_key = os.environ.get("DICT_KEY")
        if dict_app_id and dict_key:
            dict_client = dict_client_class.OxfordDictionaryClient(dict_app_id, dict_key)
        else:
            logger.error(
                "Can't use 'oxforddict', env variables 'DICT_APP_ID' or 'DICT_KEY' are not defined",
            )
    else:
        dict_client = dict_client_class()
    if not dict_client:
        logger.error(
            "Can't initialize dictionary client"
        )
        sys.exit(1)

    # Initialize image searcher
    gis_api_key = os.environ.get("GIS_API_KEY")
    search_cx = os.environ.get("SEARCH_CX")
    if gis_api_key and search_cx:
        image_searcher = ImageSearcher(gis_api_key, search_cx)
    else:
        logger.warning(
            "Env variables 'GIS_API_KEY' or 'SEARCH_CX' are not defined"
            + "will not add images to words"
        )
        image_searcher = None

    kobo = kobo_reader.KoboReader(kobo_path)
    logger.debug("Initialized Kobo reader with kobo DB path: %s", kobo_path)

    language_processor = LanguageProcessor()
    logger.info("Initialized language processor")

    anki_deck_generator = anki.AnkiDeck(deck_name, image_searcher)

    if exclude_words_path:
        with open(exclude_words_path, 'r', encoding="utf-8") as fh:
            exclude_words = set(map(lambda x: x.strip(), fh.readlines()))
        for exclude_word in exclude_words:
            exclude_words.add(language_processor.lemmatize_word(exclude_word))
    else:
        exclude_words = []

    main(
        dict_client,
        kobo,
        anki_deck_generator,
        language_processor,
        output_deck_path,
        limit,
        image_searcher,
        words_to_exclude=set(exclude_words)
    )


def main(
        dict_client: DictClient,
        kobo_db: KoboDBReaderProtocol,
        anki_deck_generator: anki.AnkiDeck,
        language_processor: LanguageProcessor,
        output_deck_path: str,
        limit: int,
        image_searcher: Optional[ImageSearcher],
        words_to_exclude: Optional[Set[str]]
):
    # language_processor = LanguageProcessor()
    """

    """

    words_definitions: List[model.WordDefinition] = []
    words_from_kobo = kobo_db.get_saved_words()

    # dedup words
    words_from_kobo = list(
        set(
            map(lambda x: x.lower(), words_from_kobo)
        )
    )
    logger.info("Read %d words from kobo", len(words_from_kobo))
    # exclude already processed words
    if words_to_exclude:
        words_from_kobo = list(filter(lambda x: x not in words_to_exclude, words_from_kobo))
        logger.info("After exclusion have %d words from kobo to process", len(words_from_kobo))

    logger.debug("List of words from kobo: %s", words_from_kobo)

    # to ensure random order, it is hard to memorize if all words in deck start with A for example
    random.shuffle(words_from_kobo)

    if limit > 0:
        words_limit = limit
        logger.info(
            "Limit set to %d, so will process only %d words",
            words_limit, words_limit
        )
    else:
        logger.debug("Words limit was not set, will process all words")
        words_limit = len(words_from_kobo)

    # TODO: restructure to make it simpler
    for word_from_kobo in words_from_kobo[:words_limit]:
        word_definition = None
        word_from_kobo = language_processor.lemmatize_word(word_from_kobo)
        try:
            logger.debug("Getting definition for word %s, using %s", word_from_kobo, dict_client)
            word_definition = dict_client.get_definition(word_from_kobo)

            if image_searcher:
                for explanation in word_definition.explanations:
                    if explanation.part == model.Parts.NOUN:
                        logger.info(
                            "Word %s has Noun part, will get image",
                            word_definition.word,
                        )
                        word_definition.image = image_searcher.get_image_for_word(
                            word_definition.word
                        )
                        break
            else:
                logger.debug("Will not try to get image for word %s", word_definition.word)

            words_definitions.append(word_definition)
            logger.info("Found definition for word %s using client %s", word_from_kobo, dict_client)
        except dict_errors.WordTranslationNotFound:
            logger.warning(
                "Didn't find definition for word %s, will skip the word", word_from_kobo
            )
        except dict_errors.CantParseDictData as exc:
            logger.warning("Can't parse word %s. Error %s", word_from_kobo, exc)

        except dict_errors.NotAbleToGetWordTranlsation as exc:
            logger.warning("Can't get word %s. Err: %s", word_from_kobo, exc)

        if word_definition is None:
            logger.error("Didn't find word definition for word %s", word_from_kobo)

    if words_definitions:
        logger.debug("Going to generate anki deck for %d words", len(words_definitions))
        anki_deck_generator.generate_and_save_deck(words_definitions, output_deck_path)
        logger.info(
            "Saved deck with %d words to %s",
            len(words_definitions),
            output_deck_path
        )
    else:
        raise RuntimeError("No words definitions found, skip generation of anki deck")


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
