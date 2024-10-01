import papier
from typing import Any


@papier.extractor()
def read_tags(document: papier.Document, tags: dict[str, Any]
              ) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract the tags already present in the document, removing the
    prepended '/' and turning the key to lowercase"""
    meta = document.pdfreader.metadata

    res = {}
    for key, value in meta.items():
        converted_key = ''
        if key.startswith('/'):
            converted_key = key[1:].lower()
        if converted_key != '':
            res[converted_key] = value

    return (res, {})
