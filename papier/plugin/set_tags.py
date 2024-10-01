import papier
import confuse
from typing import Any


@papier.extractor()
def set_tags(document: papier.Document, tags: dict[str, Any]
             ) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        return (papier.config['import']['set'].get(dict), {})
    except confuse.ConfigError:
        return ({}, {})
