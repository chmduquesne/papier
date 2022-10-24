"""Support for papier plugins"""

import logging
import traceback
import importlib
from collections import defaultdict



# Global logger
log = logging.getLogger('papier')


# Map event name -> list of functions to call
_listeners = defaultdict(list)



def register_listener(event, func):
    """Sets func to be called whenever the event is triggered"""
    _listeners[event].append(func)



def send(event, *args, **kwds):
    """Call all functions registered for the event"""
    log.info(f'Sending event: {event}')
    for func in _listeners[event]:
        log.info(f'Calling function: {func.__name__}(args={args}, kwds={kwds})')
        func(*args, **kwds)



def load_plugins(plugins=()):
    for plugin in plugins:
        modname = f'papier.plugin.{plugin}'
        try:
            log.info(f'loading plugin {plugin}')
            module = importlib.import_module(modname)
            if hasattr(module, 'configure_me'):
                module.configure_me()
        except ModuleNotFoundError as exc:
            log.warning(f'** plugin {plugin} not found')
        except Exception:
            log.warning(f'** error loading plugin "{plugin}":\n{traceback.format_exc()}')
