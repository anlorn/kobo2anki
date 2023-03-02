# Card's front(part with a question)
FRONT_TEMPLATE = '<p class="question">{{Word}} [<b>{{Part}}</b>]</p>'

# Card's back(part with an answer)
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

# Card's style
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

# Card's fields
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
