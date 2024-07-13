from typing import List


class FakeKoboReader:
    def __init__(self, words_to_return: List[str]):
        self.words_to_return = words_to_return

    def get_saved_words(self):
        return self.words_to_return
