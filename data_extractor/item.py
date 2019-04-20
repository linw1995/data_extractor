# Standard Library
import warnings

from typing import Any, Dict, Iterator, List, Tuple

# Local Folder
from .abc import AbstractExtractor, sentinel


class FieldMeta(type):
    def __init__(cls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]):
        super().__init__(name, bases, attr_dict)
        field_names: List[str] = []
        for key, attr in attr_dict.items():
            if isinstance(type(attr), FieldMeta):
                field_names.append(key)

        cls._field_names = field_names


class Field(metaclass=FieldMeta):
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
        return f"{self.__class__.__name__}(extractor={self.extractor!r}, default={self.default!r}, is_many={self.is_many})"

    def extract(self, element: Any) -> Any:
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
                raise ValueError(f"Invalid {self!r}")

            return self.default

        return self._extract(rv[0])

    def _extract(self, element: Any) -> Any:
        return element

    @classmethod
    def field_names(cls) -> Iterator[str]:
        for name in cls._field_names:
            yield name


class Item(Field):
    def _extract(self, element: Any) -> Any:
        rv = {}
        for field in self.field_names():
            rv[field] = getattr(self, field).extract(element)

        return rv


__all__ = ("Field", "FieldMeta", "Item")
