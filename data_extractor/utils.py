"""
=================================
:mod:`utils` -- Extracting Utils.
=================================
"""
# Standard Library
import inspect

from types import FrameType
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, TypeVar


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
    # Local Folder
    from .abc import AbstractComplexExtractor, AbstractSimpleExtractor

    return isinstance(obj, (AbstractComplexExtractor, AbstractSimpleExtractor))


def is_simple_extractor(obj: Any) -> bool:
    """
    Determine the object if it is a simple extractor, return :obj:`True` if it is.
    """
    # Local Folder
    from .abc import AbstractSimpleExtractor

    return isinstance(obj, AbstractSimpleExtractor)


def is_complex_extractor(obj: Any) -> bool:
    """
    Determine the object if it is a complex extractor, return :obj:`True` if it is.
    """
    # Local Folder
    from .abc import AbstractComplexExtractor

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


class Property(Generic[T]):
    """
    Extractor property.

    :param name: The actual name of the property where value is stored.
    :type name: Optional[str]
    """

    def __set_name__(self, owner: Any, name: str):
        """
        Customized names -- Descriptor HowTo Guide
        https://docs.python.org/3/howto/descriptor.html#customized-names
        """
        self.public_name = name
        self.pravite_name = f"__property_{name}"

    def __get__(self, obj: Any, cls: Any) -> T:
        if obj is None:
            return self

        try:
            return getattr(obj, self.pravite_name)
        except AttributeError as exc:
            # raise right AttributeError
            msg: str = exc.args[0]
            raise AttributeError(msg.replace(self.pravite_name, self.public_name))

    def __set__(self, obj: Any, value: T) -> T:
        return setattr(obj, self.pravite_name, value)


if TYPE_CHECKING:
    # Local Folder
    from .abc import AbstractExtractors


class BuildProperty(Property[T]):
    """
    Extractor property is part of the function of extracting.
    When it gets modified, it will unbuild its extractor.

    :param name: The actual name of the property where value is stored.
    :type name: Optional[str]
    """

    def __set__(self, obj: "AbstractExtractors", value: T) -> T:
        obj.built = False
        return super().__set__(obj, value)


def _missing_dependency(dependency: str) -> None:
    """
    Raise :class:RuntimeError for the extractor class that missing optional dependency.
    """
    raise RuntimeError(f"{dependency!r} package is needed, run pip to install it. ")


__all__ = (
    "LazyStr",
    "BuildProperty",
    "Property",
    "getframe",
    "is_complex_extractor",
    "is_extractor",
    "is_simple_extractor",
    "sentinel",
)
