"""Support for papier plugins"""

import papier.errors
import logging
import traceback
import importlib
from collections import defaultdict
from typing import Any, Callable


# Global logger
log = logging.getLogger('papier')


# Map event name -> list of functions to call
_event_handlers = defaultdict(set)


# Map event name -> description
_event_descriptions = defaultdict(str)


def declare_event(event: str, description: str) -> None:
    if event in _event_descriptions:
        raise papier.PluginError(f'Event "{event}" already declared')
    _event_descriptions[event] = description


def set_event_handler(event: str, func: Callable) -> None:
    """Sets func to be called whenever the event is triggered"""
    if event not in _event_descriptions:
        raise papier.PluginError(f'Event "{event}" is not declared')
    _event_handlers[event].add(func)


def send_event(event: str, *args: tuple[Any], **kwds: dict[str, Any]
               ) -> None:
    """Call all functions registered for the event"""
    if event not in _event_descriptions:
        raise papier.PluginError(f'Event "{event}" is not declared')
    log.info(f'Sending event: {event}')
    for func in _event_handlers[event]:
        log.info(f'Calling function: '
                 f'{func.__name__}(args={args}, kwds={kwds})')
        func(*args, **kwds)


def load_plugins(plugins: list[str] = ()) -> None:
    for plugin in plugins:
        modname = f'papier.plugin.{plugin}'
        try:
            log.info(f'loading plugin {plugin}')
            importlib.import_module(modname)
        except ModuleNotFoundError:
            log.warning(f'** plugin {plugin} not found')
        except Exception:
            log.warning(
                    f'** error loading plugin "{plugin}":\n'
                    f'{traceback.format_exc()}'
                    )
