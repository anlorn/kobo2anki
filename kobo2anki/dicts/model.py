from typing import List, Optional
from enum import Enum
from dataclasses import dataclass


class Parts(Enum):
    VERB = "verb"
    ADJ = "adj"
    NOUN = "noun"


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
class DictWord:
    word: str
    transcription: str
    explanations: List[PartExplanations]
    audio_file_path: Optional[str] = None
