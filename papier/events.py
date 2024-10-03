"""Support for papier events"""
# TODO is this necessary?
import papier
from typing import Dict


_events = dict()


def document_event(name: str, description: str) -> None:
    if name in _events:
        raise papier.PluginError(f'{name} is already a documented event')
    _events[name] = description


def documented_events() -> Dict[str, str]:
    return dict(_events)
