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



def send(event, *args, **kwargs):
    """Call all functions registered for the event"""
    for func in _listeners[event]:
        func(*args, **kwargs)



class ModuleWrapper:
    def __init__(self, module):
        self.module = module


    def myfunc(self):
        if hasattr(self.module, 'myfunc'):
            self.module.myfunc()



def load_plugins(names=()):
    for name in names:
        modname = f'papier.plugin.{name}'
        try:
            module = ModuleWrapper(importlib.import_module(modname))
        except ModuleNotFoundError as exc:
            log.warning(f'** plugin {name} not found')
        except Exception:
            log.warning(f'** error loading plugin {name}:\n{traceback.format_exc()}')
    send('plugins loaded')
