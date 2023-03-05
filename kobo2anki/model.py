from typing import List, Optional
from enum import Enum
from dataclasses import dataclass


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
    audio_file_path: Optional[str] = None
