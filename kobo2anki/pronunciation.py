import os
import logging
import requests
from urllib.parse import urlparse

from kobo2anki import errors
from kobo2anki.caching import LocalFSCaching

logger = logging.getLogger(__name__)


class WordPronunciation:

    cache_entity = "wp"

    def __init__(self, url: str):
        self._url = url
        self._cache_handler = LocalFSCaching()

    def _get_filename(self) -> str:
        filename = urlparse(self._url).path.split('/')[-1]
        return filename

    def _download_audio_data(self) -> bytes:
        logger.debug(
            "Going to download audio data from url %s", self._url
        )
        response = requests.get(self._url)
        if 200 <= response.status_code < 300:
            audio_data = response.content
            if len(audio_data) > 0:
                logger.debug(
                    "Got succesfull response with status %s and number of bytes %d",
                    response.status_code,
                    len(audio_data)
                )
                return audio_data
            else:
                raise errors.GettingPronunciationError(
                    f"Url {self._url} response has status code {response.status_code}, but no content",
                )

        else:
            raise errors.GettingPronunciationError(
                f"Url {self._url} response has error status code {response.status_code}",
            )

    def _save_audio_data(self, fullpath: str, audio_data: bytes):
        if os.path.exists(fullpath):
            raise errors.SavingPronunciationError(
                f"Can't save pronunciation to {fullpath} file already exists"
            )

        path, _ = os.path.split(fullpath)
        if not os.path.exists(path):
            raise errors.SavingPronunciationError(
                f"Can't save pronunciation to {path}, because folder doesn't exists"
            )

        with open(fullpath, 'wb') as wh:
            wh.write(audio_data)
        logger.debug("Save %d bytes to %s", len(audio_data), fullpath)

    def save_audio_file_to(self, fullpath: str):
        """
        FullPath to save file should include filename
        """
        cache_key = self._get_filename()
        audio_data = self._cache_handler.get_cached_data(self.cache_entity, cache_key)
        if not audio_data:
            logger.debug("No pronunciation cache for %s, will download data", cache_key)
            audio_data = self._download_audio_data()
            self._cache_handler.save_data_to_cache(self.cache_entity, cache_key, audio_data)
        logger.debug(
            "Going to save audio_data from url %s to %s",
            self._url,
            fullpath,
        )
        self._save_audio_data(fullpath, audio_data)
