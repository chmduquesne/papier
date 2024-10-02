import papier
from typing import Any
import spacy
import logging


# Get rid of the annoying message about padding to max length from
# transformers/tokenization_utils_base.py
logging.getLogger('transformers.tokenization_utils_base').setLevel(logging.CRITICAL)


@papier.extractor(consumes=['lang'], produces=['emmitter'])
def extract_emmitter(document: papier.Document, tags: dict[str, Any]
                     ) -> tuple[dict[str, Any], dict[str, Any]]:
    if 'lang' not in tags:
        return {}
    lang = tags['lang']

    emmitter = ''

    gliner_config = {
            'gliner_model': 'gliner-community/gliner_small-v2.5',
            'chunk_size': 250,
            'labels': ['person', 'company'],
            'style': 'ent'
            }

    nlp = spacy.blank(lang)
    nlp.add_pipe('gliner_spacy', config=gliner_config)

    for part in document.important_parts():
        doc = nlp(part)
        for ent in doc.ents:
            if ent.label_ == 'company':
                emmitter = ent.text
                break
        if emmitter:
            break
    return ({'emmitter': emmitter}, {})
