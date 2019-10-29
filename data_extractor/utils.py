"""
:mod:`utils` -- Extracting Utils.
=================================
"""
# Standard Library
import inspect

from types import FrameType
from typing import Any, Callable, Optional


class __Sentinel:
    """ Singleton. """

    def __repr__(self) -> str:
        return "sentinel"


sentinel = __Sentinel()


class LazyStr:
    """
    Lazy String.

    :param func: Lazy __str__ function.
    """

    def __init__(self, func: Callable[[], str]):
        self.func = func

    def __str__(self) -> str:
        return self.func()


def is_extractor(obj: Any) -> bool:
    """
    Determine the object if it is an extractor, return :obj:`True` if it is.
    """
    from .abc import AbstractSimpleExtractor, AbstractComplexExtractor

    return isinstance(obj, (AbstractComplexExtractor, AbstractSimpleExtractor))


def is_simple_extractor(obj: Any) -> bool:
    """
    Determine the object if it is a simple extractor, return :obj:`True` if it is.
    """
    from .abc import AbstractSimpleExtractor

    return isinstance(obj, AbstractSimpleExtractor)


def is_complex_extractor(obj: Any) -> bool:
    """
    Determine the object if it is a complex extractor, return :obj:`True` if it is.
    """
    from .abc import AbstractComplexExtractor

    return isinstance(obj, AbstractComplexExtractor)


def getframe(depth: int = 0) -> Optional[FrameType]:
    frame = inspect.currentframe()
    if frame is None:
        # If running in an implementation without Python stack frame support,
        return None

    while depth > -1:
        frame = frame.f_back
        depth -= 1

    return frame


__all__ = (
    "LazyStr",
    "getframe",
    "is_complex_extractor",
    "is_extractor",
    "is_simple_extractor",
    "sentinel",
)
