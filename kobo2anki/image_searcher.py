import os
import logging
import requests
import tempfile
import googleapiclient
from typing import Optional
from google_images_search import GoogleImagesSearch

from kobo2anki.caching import LocalFSCaching


logger = logging.getLogger(__name__)


class WordImage:

    def __init__(self, filename: str, data: bytes):
        self._filename = filename
        self._data = data

    def get_filename(self) -> str:
        return self._filename

    def save_image_to(self, fullpath: str):
        path, _ = os.path.split(fullpath)
        if not os.path.exists(path):
            raise RuntimeError(
                f"Can't save pronunciation to {path}, \
                 because folder doesn't exists"
            )

        with open(fullpath, 'wb') as wh:
            wh.write(self._data)


class ImageSearcher:

    cache_entity = "images"

    def __init__(self, api_key: str, custom_search_cx: str):
        self._cache = LocalFSCaching()
        self._tempdir = tempfile.mkdtemp()
        self._gis = GoogleImagesSearch(api_key, custom_search_cx)

    def get_image_for_word(self, word: str) -> Optional[WordImage]:
        cache_filename = f"{word}.jpg"
        cached_image = self._cache.get_cached_data(self.cache_entity, cache_filename)
        if cached_image:
            return WordImage(cache_filename, cached_image)
        else:
            # Define the search params
            search_params = {
                'q': f"{word}",
                'num': 1,
                'fileType': 'jpg',
                'safe': 'medium',
            }

            # Search for the image
            try:
                self._gis.search(search_params)

                for result in self._gis.results():
                    self._cache.save_data_to_cache(self.cache_entity, cache_filename, result.get_raw_data())
                    return WordImage(cache_filename, result.get_raw_data())
            except googleapiclient.errors.HttpError as exc:
                logger.warning("Can't get image for word %s, err %s", word, str(exc))

        return None
