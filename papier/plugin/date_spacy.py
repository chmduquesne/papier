import papier
import spacy
from typing import Any


@papier.extractor(consumes=['lang'], produces=[''])
def extract_date(document: papier.Document, tags: dict[str, Any]
                 ) -> tuple[dict[str, Any], dict[str, Any]]:
    if 'lang' not in tags or tags['lang'] != 'en':
        return ({'date': 'XXXX-XX-XX'}, {})

    nlp = spacy.blank('en')
    nlp.add_pipe('find_dates')

    doc = nlp(document.text)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            date = ent._.date[:10]
            return ({'date': date}, {})
    return ({}, {})
