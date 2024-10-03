import papier
from typing import Callable, List, Set, Self, Dict, Any
import collections
from dataclasses import dataclass, field
import functools


@dataclass
class Extractor():
    """Extracts information from a document, possibly leveraging the
    result of previous extractors"""
    extract: Callable = field(repr=False)
    plugin: str = field(default='', init=False)
    consumes: List[str]
    produces: List[str]

    def __post_init__(self: Self) -> None:
        self.plugin = self.extract.__module__.split('.')[-1]


# List of registered extractors
extractors: List[Extractor] = []

# Map plugins to the tags they extract
plugins = collections.defaultdict(list)


def unsatisfied(extractors: List[Extractor]) -> int:
    """unsatisfied dependencies if the extractors are processed in order"""
    produced: Set[str] = set()
    res = 0
    for e in extractors:
        for tag in e.consumes:
            if tag not in produced:
                res += 1
        for tag in e.produces:
            produced.add(tag)
    return res


def register_extractor(e: Extractor) -> None:
    def score(i: int) -> int:
        """Number of unsatisfied dependencies for the list where e is
        inserted in the position i"""
        return unsatisfied(extractors[:i] + [e] + extractors[i:])

    # Index of insertion with the minimal score
    index_min = min(range(len(extractors) + 1), key=score)

    # A plugin shall not register 2 extractors for the same tag
    plugin = e.plugin
    for tag in e.produces:
        if tag not in plugins[plugin]:
            plugins[plugin].append(tag)
        else:
            raise papier.PluginError(
                    f'{plugin} registers 2 extractors for "{tag}"')

    extractors.insert(index_min, e)


def extractor(produces: List[str] = [], consumes: List[str] = []
              ) -> Callable:
    """Register a function as an extractor, positioning it so that
    unsatisfied dependencies are minimized"""
    def decorator(func: Callable[[papier.Document, Dict[str, Any]],
                                 Dict[str, Any]]) -> Callable:
        register_extractor(Extractor(func, consumes, produces))

        @functools.wraps
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper
    return decorator
