# Standard Library
from abc import ABC, abstractmethod
from typing import Any


class __Sentinel:
    def __repr__(self) -> str:
        return "sentinel"


sentinel = __Sentinel()


class AbstractExtractor(ABC):
    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    @abstractmethod
    def extract(self, element: Any) -> Any:
        raise NotImplementedError

    def extract_first(self, element: Any, default: Any = sentinel) -> Any:
        rv = self.extract(element)
        assert isinstance(rv, list), f"Can't extract first item from result {rv!r}"

        if not rv:
            if default is sentinel:
                raise ValueError(f"Invalid {self!r}")

            return default

        return rv[0]


__all__ = ("AbstractExtractor", "sentinel")
