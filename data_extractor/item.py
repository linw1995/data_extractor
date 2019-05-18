"""
:mod:`item` -- Complex Extractor for data extracting.
=====================================================
"""
# Standard Library
import warnings

from typing import Any, Iterator

# Local Folder
from .abc import AbstractExtractor, SimpleExtractorBase
from .exceptions import ExtractError
from .utils import sentinel


class Field(AbstractExtractor):
    """
    Extract data by cooperating with extractor.

    :param extractor: The object for data extracting base on :class:`data_extractor.abc.SimpleExtractor`.
    :param name: Optional parameter for special field name.
    :param default: Default value when not found. Default: :data:`data_extractor.utils.sentinel`.
    :param is_many: Indicate the data which extractor extracting is more than one.

    :raises ValueError: Invalid SimpleExtractor.
    :raises ValueError: Can't both set default and is_manay=True.
    """

    def __init__(
        self,
        extractor: SimpleExtractorBase,
        name: str = None,
        default: Any = sentinel,
        is_many: bool = False,
    ):
        if not isinstance(extractor, SimpleExtractorBase):
            raise ValueError(f"Invalid SimpleExtractor: {extractor!r}")

        if default is not sentinel and is_many:
            raise ValueError(f"Can't both set default={default} and is_many=True")

        self.extractor = extractor
        self.name = name
        self.default = default
        self.is_many = is_many

    def __repr__(self) -> str:
        args = [f"{self.extractor!r}"]
        if self.name is not None:
            args.append(f"name={self.name!r}")

        if self.default is not sentinel:
            args.append(f"default={self.default!r}")

        if self.is_many:
            args.append(f"is_many={self.is_many!r}")

        return f"{self.__class__.__name__}({', '.join(args)})"

    def extract(self, element: Any) -> Any:
        """
        Extract the wanted data.

        :param element: The target data node element.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExtractError: Thrown by extractor extracting wrong data.
        """
        rv = self.extractor.extract(element)
        if not isinstance(rv, list):
            if self.is_many:
                warnings.warn(
                    f"Expr of {self!r} conflict wiht parameter is_many=True",
                    UserWarning,
                )

            return rv

        if self.is_many:
            return [self._extract(r) for r in rv]

        if not rv:
            if self.default is sentinel:
                raise ExtractError(self, element)

            return self.default

        return self._extract(rv[0])

    def _extract(self, element: Any) -> Any:
        return element


class Item(Field):
    """
    Extract data by cooperating with extractors, fields and items.
    """

    def _extract(self, element: Any) -> Any:
        rv = {}
        for field in self.field_names():
            try:
                extractor = getattr(self, field)
                if extractor.name is not None:
                    field = extractor.name

                rv[field] = extractor.extract(element)
            except ExtractError as exc:
                exc._append(extractor=self)
                raise exc

        return rv

    @classmethod
    def field_names(cls) -> Iterator[str]:
        """
        Iterate all `Item` or `Field` type attributes' name.
        """
        for name in cls._field_names:
            yield name


__all__ = ("Field", "Item")
