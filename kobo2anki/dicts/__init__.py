from typing import Protocol, runtime_checkable
from kobo2anki.dicts.freedict import client as freedict_client
from kobo2anki.model import WordDefinition
from kobo2anki.dicts.oxforddictionaries import client as of_client


CLIENTS = {
    "oxforddict": of_client,
    "freedict": freedict_client
}


@runtime_checkable
def DictClient(Protocol):
    def get_definition(self, word: str) -> WordDefinition:
        pass