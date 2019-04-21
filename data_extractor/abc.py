"""
Abstract Base Classes.
"""
# Standard Library
import warnings

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
        """
        Extract data or subelement from element.
        """
        raise NotImplementedError

    def extract_first(self, element: Any, default: Any = sentinel) -> Any:
        """
        Extract the first data or subelement from `extract` method call result.
        """
        rv = self.extract(element)
        if not isinstance(rv, list):
            warnings.warn(
                f"{self!r} can't extract first item from result {rv!r}", UserWarning
            )
            return rv

        if not rv:
            if default is sentinel:
                raise ValueError(f"Invalid {self!r}")

            return default

        return rv[0]


__all__ = ("AbstractExtractor", "sentinel")
