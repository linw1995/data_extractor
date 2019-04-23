"""
Complex Extractor for data extracting.
"""
# Standard Library
import warnings

from typing import Any, Iterator

# Local Folder
from .abc import AbstractExtractor
from .exceptions import ExtractError
from .utils import sentinel


class Field(AbstractExtractor):
    """
    Extract data by cooperating with extractor.
    """

    def __init__(
        self,
        extractor: AbstractExtractor,
        default: Any = sentinel,
        is_many: bool = False,
    ):
        if default is not sentinel and is_many:
            raise ValueError(f"can't set default={default} when is_many=True")

        self.extractor = extractor
        self.default = default
        self.is_many = is_many

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.extractor!r}, default={self.default!r}, is_many={self.is_many})"

    def extract(self, element: Any) -> Any:
        """
        Extract the wanted data.
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
                rv[field] = getattr(self, field).extract(element)
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
