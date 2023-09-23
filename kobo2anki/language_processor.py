import nltk
nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer


class LanguageProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def lemmatize_word(self, word: str) -> str:
        base_word = self.lemmatizer.lemmatize(word)
        return base_word
