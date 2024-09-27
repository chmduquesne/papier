from typing import NamedTuple, Any, Self


class Tag(NamedTuple):
    name: str
    type: str
    value: str
    confidence: float

    @classmethod
    def from_values(name: str, type: str, value: Any, confidence: float
                    ) -> Self:
        possible_types = ('scalar', 'date', 'category')
        if type not in possible_types:
            raise ValueError(f'type(={type}) must be one of {possible_types}')
        return Tag(name, type, str(value), confidence)
