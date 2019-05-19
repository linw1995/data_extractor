"""
:mod:`utils` -- Extracting Utils.
=================================
"""
# Standard Library
from typing import Callable


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


__all__ = ("LazyStr", "sentinel")
