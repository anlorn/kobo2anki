import os
import re
import logging
from typing import List, Optional

from kobo2anki.kobo import errors, db

logger = logging.getLogger(__name__)


class KoboReader:

    def __init__(self, mount_path: str):
        self._mount_path = mount_path
        if not os.path.exists(self._mount_path):
            raise errors.KoboDataNotFound(
                f"Path {self._mount_path} doesn't exists"
            )
        logger.debug("Look for kobo data in folder - %s", self._mount_path)
        self._db_handler = db.KoboDB(
            os.path.join(self._mount_path, ".kobo/KoboReader.sqlite")
        )

    def get_saved_words(self) -> List[str]:
        words = []  # type: List[str]
        dict_words = self._db_handler.get_dict_words()
        logger.info("Got %d saved dict words from kobo", len(dict_words))
        words.extend(filter(
            None,
            map(lambda x: self._extract_word(x.text), dict_words)
        ))
        logger.debug("Added %d words after cleaning", len(words))

        highlights = self._db_handler.get_highlights()
        logger.info("Got %d highlights from kobo", len(highlights))
        words.extend(filter(
            None,
            map(lambda x: self._extract_word(x.text), highlights)
        ))
        logger.debug("Added %d more words after cleaning", len(words))
        return list(tuple(words))

    def _extract_word(self, sentence: str) -> Optional[str]:

        # split sentence into parts by non word chars
        parts = re.split(r"\W+", sentence)
        logger.debug(
            "Split string %s into parts %s", sentence, parts
        )

        # filter out parts shorter than 3 chars
        words = list(filter(lambda x: len(x) > 2, parts))
        logger.debug(
            "We identified following words in the sentence: %s",
            words
        )
        if len(words) == 1:
            logger.debug(
                "Identified string as a word '%s'", words[0]
            )
            return words[0]
        else:
            logger.debug("String is not a single word")
            return None
