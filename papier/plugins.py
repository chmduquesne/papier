"""Support for papier plugins"""

import logging
import traceback
import importlib
from collections import defaultdict
from typing import Any, Callable


# Global logger
log = logging.getLogger('papier')


# Map event name -> list of functions to call
_event_handlers = defaultdict(set)


def register_handler(event: str, func: Callable) -> None:
    """Sets func to be called whenever the event is triggered"""
    _event_handlers[event].add(func)


def send_event(event: str, *args: tuple[Any], **kwds: dict[str, Any]
               ) -> None:
    """Call all functions registered for the event"""
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


def event_handler(event: str) -> Callable:
    """Decorator. Call this function every time the event is triggered"""
    def decorator(func: Callable) -> None:
        register_handler(event, func)
    return decorator
