import papier
from typing import NamedTuple, Callable, List, Set, Self, Dict, Any


class Extractor(NamedTuple):
    """Extracts information from a document, possibly leveraging the
    result of previous extractors"""
    extract: Callable
    consumes: List[str]
    produces: List[str]

    def __repr__(self: Self) -> str:
        return ('Extractor('
                f'{self.extract.__module__}.{self.extract.__name__}, '
                f'consumes={self.consumes}, '
                f'produces={self.produces})')


# List of registered extractors
extractors: List[Extractor] = []


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
    extractors.insert(index_min, e)


def extractor(produces: List[str] = [], consumes: List[str] = []
              ) -> Callable:
    """Register a function as an extractor, positioning it so that
    unsatisfied dependencies are minimized"""
    def decorator(func: Callable[[papier.Document, Dict[str, Any]],
                                 Dict[str, Any]]) -> None:
        register_extractor(Extractor(func, consumes, produces))
    return decorator
