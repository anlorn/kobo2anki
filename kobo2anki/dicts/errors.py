class WordTranslationNotFound(Exception):

    def __init__(self, word: str):
        msg = f"Can't find word {word}"
        super().__init__(msg)


class NotAbleToGetWordTranlsation(Exception):

    def __init__(self, word: str, err: str):
        msg = f"Can't get word '{word}' translation. Err: {err} "
        super().__init__(msg)


class CantParseDictData(Exception):
    def __init__(self, details: str):
        msg = f"Can't parse dictionary response. Err {details}"
        super().__init__(msg)
