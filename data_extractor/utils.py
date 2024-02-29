"""
=================================
:mod:`utils` -- Extracting Utils.
=================================
"""

# Standard Library
import inspect

from types import FrameType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)


class __Sentinel:
    """Singleton."""

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
    # Local Folder
    from .core import AbstractComplexExtractor, AbstractSimpleExtractor

    return isinstance(obj, (AbstractComplexExtractor, AbstractSimpleExtractor))


def is_simple_extractor(obj: Any) -> bool:
    """
    Determine the object if it is a simple extractor, return :obj:`True` if it is.
    """
    # Local Folder
    from .core import AbstractSimpleExtractor

    return isinstance(obj, AbstractSimpleExtractor)


def is_complex_extractor(obj: Any) -> bool:
    """
    Determine the object if it is a complex extractor, return :obj:`True` if it is.
    """
    # Local Folder
    from .core import AbstractComplexExtractor

    return isinstance(obj, AbstractComplexExtractor)


def getframe(depth: int = 0) -> Optional[FrameType]:
    cur = frame = inspect.currentframe()
    if frame is None:
        # If running in an implementation without Python stack frame support,
        return None

    while depth > -1:
        if cur is None:
            raise ValueError(f"Invalid depth = {depth!r} for frame = {frame!r}")

        cur = cur.f_back
        depth -= 1

    return cur


T = TypeVar("T")

if TYPE_CHECKING:
    # Local Folder
    from .core import AbstractExtractors


class Property(Generic[T]):
    """
    Extractor property.
    """

    def __set_name__(self, owner: Any, name: str) -> None:
        """
        Customized names -- Descriptor HowTo Guide
        https://docs.python.org/3/howto/descriptor.html#customized-names
        """
        self.public_name = name
        self.private_name = f"__property_{name}"

    @overload
    def __get__(self, obj: None, cls: Type["AbstractExtractors"]) -> "Property[T]":
        pass

    @overload
    def __get__(self, obj: Any, cls: Type["AbstractExtractors"]) -> T:
        pass

    def __get__(
        self, obj: Any, cls: Type["AbstractExtractors"]
    ) -> Union["Property[T]", T]:
        if obj is None:
            return self

        try:
            return getattr(obj, self.private_name)
        except AttributeError as exc:
            # raise right AttributeError
            msg: str = exc.args[0]
            raise AttributeError(msg.replace(self.private_name, self.public_name))

    def __set__(self, obj: Any, value: T) -> T:
        if hasattr(obj, self.private_name):
            raise AttributeError("can't set attribute")
        else:
            setattr(obj, self.private_name, value)
            return value

    @staticmethod
    def change_internal_value(
        obj: "AbstractExtractors", property_name: str, value: T
    ) -> None:
        attr = getattr(type(obj), property_name)
        if not isinstance(attr, Property):
            raise AttributeError(f"Type of attribute {property_name!r} is not Property")

        setattr(obj, attr.private_name, value)


def _missing_dependency(dependency: str) -> None:
    """
    Raise :class:RuntimeError for the extractor class that missing optional dependency.
    """
    raise RuntimeError(f"{dependency!r} package is needed, run pip to install it. ")


__all__ = (
    "LazyStr",
    "Property",
    "getframe",
    "is_complex_extractor",
    "is_extractor",
    "is_simple_extractor",
    "sentinel",
)
