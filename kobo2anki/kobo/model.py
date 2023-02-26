from dataclasses import dataclass


@dataclass(order=True)
class DictWord:
    text: str
    dict_suffix: str


@dataclass(order=True)
class HighLight:
    id: str
    text: str
