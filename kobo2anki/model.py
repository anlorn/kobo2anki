from typing import List, Optional
from enum import Enum
from dataclasses import dataclass

from kobo2anki.pronunciation import WordPronunciation
from kobo2anki.image_searcher import WordImage


class Parts(Enum):
    VERB = "verb"
    ADJECTIVE = "adjective"
    NOUN = "noun"
    ADVERB = "adverb"
    INTERJECTION = "interjection"
    PREPOSITION = "preposition"


@dataclass
class Definition:
    definitions: List[str]
    synonyms: List[str]
    examples: List[str]


@dataclass
class PartExplanations:
    part: Parts
    definitions: List[Definition]


@dataclass
class WordDefinition:
    word: str
    transcription: str
    explanations: List[PartExplanations]
    pronunciation: Optional[WordPronunciation] = None
    image: Optional[WordImage] = None
