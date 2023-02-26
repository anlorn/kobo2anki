import genanki

FRONT_TEMPLATE = '<p class="question">{{Word}} [<b>{{Part}}</b>]</p>'
CSS = '''
.card {
 font-family: arial;
 font-size: 15px;
 text-align: left;
 color: black;
 background-color: white;
}

.question {
    text-align: center;
    font-size: 25px;
}

.expl {
    color: DodgerBlue
}

ol li {
    margin: 5px;
}
'''
BACK_TEMPLATE = '''
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

FIELDS = [
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

# TODO make configurable
MODEL_ID = 1903016060

MODEL_NAME = "Learning English Model"

my_model = genanki.Model(
    model_id=MODEL_ID,
    name=MODEL_NAME,
    fields=FIELDS,
    templates=[
        {
            "name": "Basic Kobo Dict Template",
            "qfmt": FRONT_TEMPLATE,
            "afmt": BACK_TEMPLATE,
        }

    ]

)

my_note = genanki.Note(
    model=my_model,
    fields=[
        "Milk",
        "Noun",
        "Expl", "Syn", "Example",
        "Expl2", "Syn2", "Example2",
        "Expl3", "Syn3", "Example3",
        '[sound:sound.ogg]', '<img src="image.jpg">'

    ]
)


DECK_ID = 2010215544
DECK_NAME = "Cards for Kobo"

my_deck = genanki.Deck(
    deck_id=DECK_ID,
    name=DECK_NAME,
)

my_deck.add_note(my_note)
my_package = genanki.Package(my_deck)
my_package.media_files = ['sound.ogg', 'sound.mp3', 'image.jpg']
my_package.write_to_file("/tmp/test.apkg")
