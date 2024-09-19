"""Support for papier events"""
from typing import Dict


_events = dict()


def document_event(name: str, description: str) -> None:
    if name in _events:
        raise NameError(f'{name} is already a documented event')
    _events[name] = description


def documented_events() -> Dict[str, str]:
    return dict(_events)
