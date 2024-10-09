import papier
from typing import Any
import spacy
import logging
import huggingface_hub.utils


# Get rid of the annoying message from transformers/tokenization_utils_base.py
logging.getLogger('transformers.tokenization_utils_base').setLevel(
        logging.CRITICAL)

# Get rid of the download progress bars
huggingface_hub.utils.disable_progress_bars()


@papier.extracts(consumes=['lang'], produces=['emmitter'])
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
