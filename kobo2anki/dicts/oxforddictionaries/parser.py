import logging
from typing import Dict, Optional
from kobo2anki.dicts import model, errors


logger = logging.getLogger(__name__)


def parse_data(raw_data: Dict) -> model.DictWord:
    if 'id' not in raw_data:
        raise errors.CantParseDictData("Response has no ID")
    word = raw_data['id']

    transcription = _get_transcription(raw_data)

    dict_word = model.DictWord(
        word.lower(),
        transcription=transcription,
        explanations=[])

    if not raw_data['results'] or not raw_data['results'][0].get('lexicalEntries'):
        raise errors.CantParseDictData("Response missing 'lexicalEntries' data")

    for raw_lexical_entry in raw_data['results'][0]['lexicalEntries']:
        lexical_entry = _parse_word_lexical_entries(raw_lexical_entry)
        dict_word.explanations.append(lexical_entry)
    return dict_word


def _get_transcription(raw_data: Dict) -> str:
    for result in raw_data['results']:
        for lexical_entry in result.get('lexicalEntries', []):
            for entry in lexical_entry.get('entries', []):
                for pronunciation in entry.get('pronunciations', []):
                    if "American English" in pronunciation.get('dialects', []) and \
                            pronunciation.get("phoneticNotation") == "IPA":
                        return pronunciation['phoneticSpelling']
    raise errors.CantParseDictData("Can't find transcription for a word")


def get_audio_file_url(raw_data: Dict) -> Optional[str]:
    for result in raw_data['results']:
        for lexical_entry in result.get('lexicalEntries', []):
            for entry in lexical_entry.get('entries', []):
                for pronunciation in entry.get('pronunciations', []):
                    if "American English" in pronunciation.get('dialects', []) and \
                            pronunciation.get("audioFile"):
                        return pronunciation['audioFile']
    return None


def _parse_word_lexical_entries(le_data: Dict) -> model.PartExplanations:
    part = le_data.get('lexicalCategory', {}).get('id')
    if not part:
        raise errors.CantParseDictData("Lexical category is missing of wrong")
    parsed_part = getattr(model.Parts, part.upper())

    part_explanation = model.PartExplanations(parsed_part, definitions=[])

    part_entry = le_data.get('entries', [None])[0]
    if not part_entry:
        raise errors.CantParseDictData("Entries are not defined in lexicalEntry")
    if len(le_data['entries']) > 0:
        logger.info(
            "%s defintion of a word has more than 1 entries in LexicalEntries. Use first entry",
            part
        )
    senses = part_entry.get('senses', [])
    if not senses:
        raise errors.CantParseDictData("Entries has no senses definitions")

    for raw_sense in senses:
        definition = _parse_word_sense(raw_sense)
        part_explanation.definitions.append(definition)
    return part_explanation


def _parse_word_sense(raw_sense: Dict) -> model.Definition:
    defintions = raw_sense['definitions']
    if not defintions:
        raise errors.CantParseDictData(f"Sense record '{raw_sense}' has no definitions")

    synonyms = list(map(
        lambda x: x.get("text"),
        filter(
            lambda x: x.get('language') == "en" and x.get("text"),
            raw_sense.get('synonyms', [])
        )
    ))
    if not synonyms:
        logger.info("Can't find synonyms, going to skip them")

    examples = list(map(
        lambda x: x.get("text"),
        filter(
            lambda x: x.get("text"),
            raw_sense.get('examples', [])
        )
    ))

    if not examples:
        logger.info("Can't find examples, going to skip them")

    return model.Definition(definitions=defintions, synonyms=synonyms, examples=examples)
