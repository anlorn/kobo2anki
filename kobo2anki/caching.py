import os
import logging
import appdirs

from typing import Optional

logger = logging.getLogger(__name__)


class LocalFSCaching:

    def __init__(self):
        self._cache_dir = appdirs.user_cache_dir()
        logger.debug("Use '%s' as cache dir", self._cache_dir)

    def _get_cache_file_path(self, key: str, entity: str) -> str:
        file_path = os.path.join(
            self._cache_dir,
            "kobo2anki",
            entity,
            key
        )
        logger.debug(
            "Using cache path %s for key %s and entity %s", file_path,
            key, entity
        )
        return file_path

    def get_cached_data(self, entity: str, key: str) -> Optional[bytes]:
        result = None  # type: Optional[bytes]
        cache_file_path = self._get_cache_file_path(key, entity)
        try:
            with open(cache_file_path, 'rb') as fh:
                result = fh.read()
        except FileNotFoundError:
            logger.debug("Cache for %s with key %s not found", key, entity)
        return result

    def save_data_to_cache(self, entity: str, key: str, data: bytes):
        cache_file_path = self._get_cache_file_path(key, entity)
        if os.path.exists(cache_file_path):
            logger.warning(
                """Looks like we already have some cache fo key %s
                and entity %s. Will overwrite it.""",
                key, entity
            )
        else:
            cache_dir = os.path.dirname(cache_file_path)
            if not os.path.exists(cache_dir):
                logger.debug("Going to create cache dir '%s'", cache_dir)
                os.makedirs(cache_dir)

        with open(cache_file_path, "wb") as fh:
            fh.write(data)
        logger.debug("Recorded %d bytes into cache file %s", len(data), cache_file_path)
