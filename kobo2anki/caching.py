import os
import appdirs


def get_cache_path() -> str:
    return os.path.join(
        appdirs.user_cache_dir(),
        "kobo2anki"
    )
