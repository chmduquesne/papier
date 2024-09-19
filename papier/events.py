"""Support for papier events"""


_events = dict()


def document_event(name, description):
    if name in _events:
        raise NameError(f'{name} is already a documented event')
    _events[name] = description


def documented_events():
    return dict(_events)
