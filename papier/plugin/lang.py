import papier
from typing import Dict, Any
import spacy
import spacy_fastlang   # noqa: F401 # pylint: disable=unused-import

# https://stackoverflow.com/questions/66353366/cant-suppress-fasttext-warning-load-model-does-not-return
import fasttext
fasttext.FastText.eprint = lambda x: None


@papier.extractor(produces=['lang'])
def extract_lang(document: papier.Document, tags: Dict[str, Any]
                 ) -> Dict[str, Any]:
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('language_detector')
    doc = nlp(document.text)
    return {'lang': doc._.language}
