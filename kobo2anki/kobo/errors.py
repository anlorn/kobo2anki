class KoboDataNotFound(Exception):

    def __init__(self, msg: str):
        super().__init__(self, msg)


class KoboDataReadingError(Exception):

    def __init__(self, msg: str):
        error_msg = f"Can't read Kobo DB data: {msg}"
        super().__init__(self, error_msg)
