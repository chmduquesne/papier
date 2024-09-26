import papier
from typing import Dict, Any
from gliner import GLiNER


@papier.extractor(consumes=['lang'], produces=['emmitter'])
def extract_emmitter(document: papier.Document, tags: Dict[str, Any]
                     ) -> Dict[str, Any]:
    emmitter = ''

    model = GLiNER.from_pretrained('gliner-community/gliner_small-v2.5')

    labels = ['person', 'company', 'date']
    for part in document.important_parts():
        entities = model.predict_entities(part, labels)
        for entity in entities:
            if entity['label'] == 'company':
                emmitter = entity['text']
                break
        if emmitter:
            break
    return {'emmitter': emmitter}
