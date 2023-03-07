class GettingPronunciationError(Exception):
    def __init__(self, msg: str):
        super().__init__(self, msg)

class SavingPronunciationError(Exception):
    def __init__(self, msg: str):
        super().__init__(self, msg)
