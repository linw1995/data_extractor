"""
:mod:`exceptions` -- Extracting Exceptions.
===========================================
"""
# Standard Library
import reprlib

from typing import Any

# Local Folder
from .abc import AbstractExtractor
from .utils import LazyStr


class ExprError(Exception):
    """
    Invalid Expr.

    :param extractor: The object for data extracting base on :class:`data_extractor.abc.AbstractExtractor`.
    :param exc: The actual exception is thrown when extracting.
    """

    def __init__(self, extractor: AbstractExtractor, exc: Exception):
        self.extractor = extractor
        self.exc = exc

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.extractor!r}, exc={self.exc!r})"


class ExtractError(Exception):
    """
    Thrown by extractor extracting wrong data.

    :param extractor: The object for data extracting base on :class:`data_extractor.abc.AbstractExtractor`.
    :param element: The target data node element.
    """

    def __init__(self, extractor: AbstractExtractor, element: Any):
        super().__init__(LazyStr(func=lambda: self._trace_repr))
        self.element = element
        self.extractors = [extractor]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.extractors[0]!r}, element={reprlib.repr(self.element)})"

    def _append(self, extractor: AbstractExtractor) -> None:
        self.extractors.append(extractor)

    @property
    def _trace_repr(self) -> str:
        return f"{self.__repr__()}\n" + "\n".join(
            "  " * idx + "|-" + repr(extractor)
            for idx, extractor in enumerate([*self.extractors[::-1], self.element])
        )


__all__ = ("ExprError", "ExtractError")
