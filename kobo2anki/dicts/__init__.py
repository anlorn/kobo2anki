from kobo2anki.dicts.freedict import client as freedict_client
from kobo2anki.dicts.oxforddictionaries import client as of_client


CLIENTS = {
    "of_client": of_client,
    "freedict_client": freedict_client
}
