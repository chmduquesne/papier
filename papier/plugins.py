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



_provides = defaultdict(list)
_requires = defaultdict(list)
_predictors = []


def register_predictor(func, provides=None, requires=None):
    _provides[func] = provides
    _requires[func] = requires

    # order the predictor in such a way that the number of unsatisfied
    # dependencies is minimized
    _predictors = min([_predictors[:i] + [func] + _predictors[i:]
                       for i in range(len(_predictors) + 1)],
                      key=unsatisfied)


def unsatisfied(predictors):
    """number of unsatisfied dependencies at each step if a list of
    predictors is processed as is"""
    # An empty list has no unsatisfied dependency
    if len(predictors) == 0:
        return 0

    head = predictors[:-1]
    tail = predictors[-1]

    # compute the tags provided by the head
    provided = set()
    for p in head:
        for tag in _provides[p]:
            provided.add(tag)

    # add the unsatisfied dependencies from the head and the tail
    res = unsatisfied(head)
    for d in _dependencies[tail]:
        if d not in provided:
            res += 1

    return res




def predict_metadata(document, set_tags=None):
    # returns a meta
    # -> key: [(value, proba)]
    pass



def load_plugins(plugins=()):
    for plugin in plugins:
        modname = f'papier.plugin.{plugin}'
        try:
            log.info(f'loading plugin {plugin}')
            module = importlib.import_module(modname)
        except ModuleNotFoundError as exc:
            log.warning(f'** plugin {plugin} not found')
        except Exception:
            log.warning(f'** error loading plugin "{plugin}":\n{traceback.format_exc()}')
