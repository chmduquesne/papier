import pytest
import papier
import papier.extractor
from typing import Dict, Any


def test_extractors() -> None:
    @papier.extractor
    def foo() -> None:
        pass


def test_extractors_same_tag() -> None:
    """test that a module cannot register 2 extractors for the same tag"""
    with pytest.raises(papier.PluginError):
        @papier.extractor(produces=['foo'])
        def foo() -> Dict[str, Any]:
            return {}

        @papier.extractor(produces=['foo'])
        def bar() -> Dict[str, Any]:
            return {}
