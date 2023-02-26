import os
import sqlite3
import logging
from typing import List, Tuple, Optional

from kobo2anki.kobo import errors, model

logger = logging.getLogger(__name__)


class KoboDB:
    """
    Class to work with kobo sqlite db
    """

    def __init__(self, db_file_path: str):
        self._db_file_path = db_file_path
        if not os.path.exists(self._db_file_path):
            raise errors.KoboDataNotFound(
                f"Path {self._db_file_path} doesn't exists. Can't open Kobo DB"
            )
        self._con = None  # type: Optional[sqlite3.Connection]

    def _execute_query(self, query: str) -> List[Tuple]:
        if not self._con:
            self._con = sqlite3.connect(self._db_file_path)
            logger.debug(
                "Opened connection to Kobo DB - %s", self._db_file_path
            )
        logger.debug("Going to execute query: %s", query)
        cursor = self._con.cursor()
        response = cursor.execute(query)
        result = response.fetchall()
        logger.debug("Query '%s' returned %d rows", query, len(result))
        if self._con:
            self._con.close()
            self._con = None
            logger.debug("Closed connection to Kobo DB")
        return result

    def get_dict_words(self) -> List[model.DictWord]:
        res = []  # type: List[model.DictWord]
        records = self._execute_query("select Text, DictSuffix from wordlist")
        for record in records:
            res.append(
                model.DictWord(text=record[0], dict_suffix=record[1])
            )
        return res

    def get_highlights(self) -> List[model.HighLight]:
        res = []  # type: List[model.HighLight]
        records = self._execute_query(
            'select BookmarkID, Text from bookmark where Type="highlight"'
        )
        for record in records:
            res.append(
                model.HighLight(id=record[0], text=record[1])
            )
        return res
