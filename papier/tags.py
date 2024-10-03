from collections import UserDict
from typing import Any, Self
from dataclasses import dataclass, field
# TODO: unnecessary class?


@dataclass
class TagValue():
    value: Any
    type: str = field(default='category', init=False)
    confidence: float = field(default=-1.0, init=False)

    def __hash__(self: Self) -> int:
        return hash(self.value) + hash(self.type)

    def __post_init__(self: Self) -> None:
        valid_types = ('category', 'scalar')
        if self.type not in valid_types:
            raise ValueError(
                    f'type must be one of {valid_types} (got {self.type})')

    def set_confidence(self: Self, confidence: float) -> None:
        self.confidence = confidence


Tags = UserDict[str, TagValue]
