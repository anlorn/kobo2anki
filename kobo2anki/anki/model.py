import genanki
import logging
from typing import List

logger = logging.getLogger(__name__)


class AnkiModel:
    name = "Learning English Model"

    # Card's front(part with a question)
    front_template = '<p class="question">{{Word}} [<b>{{Part}}</b>]</p>'

    # Card's back(part with an answer)
    back_template = '''
        {{FrontSide}}

        <hr id=answer>
        <ol>
        <li>
            <div class="expl">{{Explanation_1}}}</div>
            {{#Synonym_1}} Synonym: {{Synonym_1}} {{/Synonym_1}}
              {{#Example_1}}
            <ul>
            <li><i>{{Example_1}}</i></li>
            </ul>
              {{/Example_1}}
        </li>
        {{#Explanation_2}}
        <li>
            <div class="expl">{{Explanation_2}}</div>
                {{#Synonym_2}} Synonym: {{Synonym_2}} {{/Synonym_2}}
              {{#Example_2}}
            <ul>
            <li><i>{{Example_2}}</i></li>
            </ul>
              {{/Example_2}}
        </li>
        {{/Explanation_2}}
        {{#Explanation_3}}
        <li>
            <div class="expl">{{Explanation_3}}</div>
                {{#Synonym_3}} Synonym: {{Synonym_3}} {{/Synonym_3}}
              {{#Example_3}}
            <ul>
            <li><i>{{Example_3}}</i></li>
            </ul>
              {{/Example_3}}
        </li>
        {{/Explanation_3}}
        </ol>

        <a href="https://www.oxfordlearnersdictionaries.com/us/definition/english/{{Word}}">check in dictionary</a>
        <hr>
        {{Picture}}
        {{Pronunciation}}
    '''

    # Card's fields
    fields = [
        {
            "name": "Word",
            "font": "Arial",
        },
        {
            "name": "Part",
            "font": "Arial Black",
        },
        {
            "name": "Explanation_1",
            "font": "Arial",
        },
        {
            "name": "Synonym_1",
            "font": "Arial",
        },
        {
            "name": "Example_1",
            "font": "Arial",
        },
        {
            "name": "Explanation_2",
            "font": "Arial",
        },
        {
            "name": "Synonym_2",
            "font": "Arial",
        },
        {
            "name": "Example_2",
            "font": "Arial",
        },
        {
            "name": "Explanation_3",
            "font": "Arial",
        },
        {
            "name": "Synonym_3",
            "font": "Arial",
        },
        {
            "name": "Example_3",
            "font": "Arial",
        },
        {
            "name": "Pronunciation",
            "font": "Arial",
        },
        {
            "name": "Picture",
            "font": "Arial",
        }
    ]

    def __init__(self):
        self._model = genanki.Model(
            model_id=self.model_id,
            name=self.name,
            fields=self.fields,
            templates=[
                {
                    "name": f"{self.name} Template",
                    "qfmt": self.front_template,
                    "afmt": self.back_template,
                }

            ]

        )

    @property
    def model_id(self):
        return '1903016060'

    def _get_ordered_fields_names(self) -> List:
        fields = filter(
            bool,
            [field.get("name") for field in self.fields]
        )
        logger.debug("Model fields names in orderd list: %s", fields)
        return list(fields)

    def generate_note(self, **fields) -> genanki.Note:
        logger.debug(
            "Got request to generate note with fields %s",
            fields
        )

        # Convert all fields names into lower
        fields = dict(
            [
                (item[0].lower(), item[1],) for item in fields.items()
            ]
        )

        # get all fields model has in an order how they defined
        ordered_model_fields = self._get_ordered_fields_names()
        # conver fields names to lower case
        ordered_model_fields = list(map(lambda x: x.lower(), ordered_model_fields))

        unknown_fields = set(fields.keys()) - set(ordered_model_fields)
        if len(unknown_fields):
            raise RuntimeError("Model doesn't have field(s): %s", unknown_fields)

        # list of fields for the note must be in the same order fields defined
        # in the model
        fields_values = []  # type: List[str]
        for model_field_name in ordered_model_fields:
            field_value = fields.get(model_field_name, "")
            fields_values.append(field_value)
        logger.debug("Will generate note with fields %s", fields_values)
        note = genanki.Note(
            model=self._model,
            fields=fields_values
        )
        return note
