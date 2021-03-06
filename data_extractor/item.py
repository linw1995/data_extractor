"""
=====================================================
:mod:`item` -- Complex Extractor for data extracting.
=====================================================
"""
# Standard Library
import copy

from typing import Any, Dict, Iterator

# Local Folder
from .abc import AbstractComplexExtractor, AbstractSimpleExtractor, BuildProperty
from .exceptions import ExtractError
from .utils import Property, is_simple_extractor, sentinel


class Field(AbstractComplexExtractor):
    """
    Extract data by cooperating with extractor.

    :param extractor: The object for data extracting
    :type extractor: :class:`data_extractor.abc.AbstractSimpleExtractor`
    :param name: Optional parameter for special field name.
    :type name: str, optional
    :param default: Default value when not found. \
        Default: :data:`data_extractor.utils.sentinel`.
    :type default: Any
    :param is_many: Indicate the data which extractor extracting is more than one.
    :type is_many: bool

    :raises ValueError: Invalid SimpleExtractor.
    :raises ValueError: Can't both set default and is_manay=True.
    """

    extractor = BuildProperty()
    name = Property()
    default = Property()
    is_many = Property()

    def __init__(
        self,
        extractor: AbstractSimpleExtractor = None,
        name: str = None,
        default: Any = sentinel,
        is_many: bool = False,
    ):
        super().__init__()

        if extractor is not None and not is_simple_extractor(extractor):
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

    def build(self) -> None:
        if self.extractor is not None:
            self.extractor.build()

        if self.__class__ is Field:
            self.built = True

    def extract(self, element: Any) -> Any:
        if not self.built:
            self.build()

        if self.extractor is None:
            if isinstance(element, list):
                rv = element
            else:
                rv = [element]
        else:
            rv = self.extractor.extract(element)

        if self.is_many:
            return [self._extract(r) for r in rv]

        if not rv:
            if self.default is sentinel:
                raise ExtractError(self, element)

            return self.default

        return self._extract(rv[0])

    def _extract(self, element: Any) -> Any:
        return element

    def __deepcopy__(self, memo: Dict[int, Any]) -> AbstractComplexExtractor:
        deepcopy_method = self.__deepcopy__
        self.__deepcopy__ = None  # type: ignore
        cp = copy.deepcopy(self, memo)
        self.__deepcopy__ = deepcopy_method  # type: ignore

        # avoid duplicating the sentinel object.
        if self.default is sentinel:
            cp.default = self.default

        return cp


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
        yield from cls._field_names

    def build(self) -> None:
        super().build()

        for extractor_name in self.field_names():
            extractor: Field = getattr(self, extractor_name)
            if not extractor.built:
                extractor.build()

        self.built = True

    def simplify(self) -> AbstractSimpleExtractor:
        """
        Create an extractor that has compatible API like SimpleExtractor's.

        :returns: A simple extractor.
        :rtype: :class:`data_extractor.abc.AbstractSimpleExtractor`
        """
        duplicated = copy.deepcopy(self)

        def build(self: AbstractSimpleExtractor) -> None:
            duplicated.build()

        def extract(self: AbstractSimpleExtractor, element: Any) -> Any:
            duplicated.is_many = True
            return duplicated.extract(element)

        def getter(self: AbstractSimpleExtractor, name: str) -> Any:
            if (
                name not in ("extract", "extract_first")
                and not name.startswith("__")
                and hasattr(duplicated.extractor, name)
            ):
                return getattr(duplicated.extractor, name)
            return super(type(self), self).__getattribute__(name)

        def setter(self: AbstractSimpleExtractor, name: str, value: Any) -> Any:
            if hasattr(duplicated.extractor, name):
                return setattr(duplicated.extractor, name, value)
            return super(type(self), self).__setattr__(name, value)

        classname = f"{type(duplicated).__name__}Simplified"
        base = AbstractSimpleExtractor
        if duplicated.extractor is not None:
            base = type(duplicated.extractor)

        return type(
            classname,
            (base,),
            {
                "build": build,
                "extract": extract,
                "__getattribute__": getter,
                "__setattr__": setter,
            },
        )(expr=duplicated.extractor.expr if duplicated.extractor is not None else None)


__all__ = ("Field", "Item")
