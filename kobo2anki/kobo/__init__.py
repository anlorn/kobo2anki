from typing import Protocol, runtime_checkable, List


@runtime_checkable
class KoboDBReaderProtocol(Protocol):  # pylint: disable=all

    def get_saved_words(self) -> List[str]:
        """
        Extract saved words from kobo sqlite DB.
        """
        pass
