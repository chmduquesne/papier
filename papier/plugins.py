"""Support for papier plugins"""

import logging
import traceback
import importlib
from collections import defaultdict
from typing import Callable, Tuple, Dict, List, Any


# Global logger
log = logging.getLogger('papier')


# Map event name -> list of functions to call
_listeners = defaultdict(list)


def register_listener(event: str, func: Callable) -> None:
    """Sets func to be called whenever the event is triggered"""
    _listeners[event].append(func)


def send(event: str, *args: Tuple[Any, ...], **kwds: Dict[str, Any]) -> None:
    """Call all functions registered for the event"""
    log.info(f'Sending event: {event}')
    for func in _listeners[event]:
        log.info(f'Calling function: '
                 f'{func.__name__}(args={args}, kwds={kwds})')
        func(*args, **kwds)


def load_plugins(plugins: List[str] = ()) -> None:
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
