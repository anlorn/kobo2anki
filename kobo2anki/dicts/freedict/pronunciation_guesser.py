from typing import Optional, Iterable
from urllib.parse import urljoin
import requests


class PronunciationURLGuesser:
    """
    Trying to buind an URL to download words pronunciation from different dicts
    """

    def get_url(self, word: str) -> Optional[str]:
        for url in self._guess_urls(word):
            if self._test_url(url):
                return url
        return None

    def _guess_urls(self, word: str) -> Iterable[str]:
        base_dicts = [
            {
                "base": "https://audio.oxforddictionaries.com/en/mp3/",
                "path_templates": [
                    "{word}__us_1.mp3",
                    "{word}__us_2.mp3",
                    "{word}__us_3.mp3",
                    "{word}-us.mp3",
                    "{word}.mp3",
                    "{word}-au.mp3",
                    "{word}-uk.mp3",
                ]
            }
        ]
        for base_dict in base_dicts:
            for path_template in base_dict["path_templates"]:
                url_template = urljoin(base_dict["base"], path_template)
                url = url_template.format(word=word)
                yield url

    def _test_url(self, url: str) -> bool:
        response = requests.head(url)
        if response.status_code >= 200 and response.status_code < 300:
            return True
        return False
