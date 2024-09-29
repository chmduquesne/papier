import papier
from typing import Callable, List, Set, Self, Dict, Any
import collections
from dataclasses import dataclass, field


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

# Map modules to the tags they extract
modules = collections.defaultdict(list)


def unsatisfied(extractors: List[Extractor]) -> int:
    """unsatisfied dependencies if the extractors are processed in order"""
    produced: Set[str] = set()
    res = 0
    for e in extractors:
        for c in e.consumes:
            if c not in produced:
                res += 1
        for p in e.produces:
            produced.add(p)
    return res


def register_extractor(e: Extractor) -> None:
    def score(i: int) -> int:
        """Number of unsatisfied dependencies for the list where e is
        inserted in the position i"""
        return unsatisfied(extractors[:i] + [e] + extractors[i:])

    # Index of insertion with the minimal score
    index_min = min(range(len(extractors) + 1), key=score)

    # A module shall not register 2 extractors for the same tag
    module = e.extract.__module__
    for p in e.produces:
        if p not in modules[module]:
            modules[module].append(p)
        else:
            raise NameError(f'{module} registers 2 extractors for "{p}"')

    extractors.insert(index_min, e)


def extractor(produces: List[str] = [], consumes: List[str] = []
              ) -> Callable:
    """Register a function as an extractor, positioning it so that
    unsatisfied dependencies are minimized"""
    def decorator(func: Callable[[papier.Document, Dict[str, Any]],
                                 Dict[str, Any]]) -> None:
        register_extractor(Extractor(func, consumes, produces))
    return decorator
