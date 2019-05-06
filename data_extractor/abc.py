"""
:mod:`abc` -- Abstract Base Classes.
====================================
"""
# Standard Library
import warnings

from abc import abstractmethod
from typing import Any, Dict, List, Tuple

# Local Folder
from .utils import sentinel


class ComplexExtractorMeta(type):
    """
    Complex Extractor Meta Class.
    """

    def __init__(cls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]):
        super().__init__(name, bases, attr_dict)
        field_names: List[str] = []
        for key, attr in attr_dict.items():
            if isinstance(type(attr), ComplexExtractorMeta):
                field_names.append(key)

        cls._field_names = field_names


class AbstractExtractor(metaclass=ComplexExtractorMeta):
    """
    All Extractors' Abstract Base Clase.

    :param expr: Extractor selector expression.
    """

    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    @abstractmethod
    def extract(self, element: Any) -> Any:
        """
        Extract data or subelement from element.

        :param element: The target data node element.

        :returns: Data or subelement
        """
        raise NotImplementedError


class SimpleExtractorBase(AbstractExtractor):
    """
    Simple Extractor Base Class.

    :param expr: extractor selector expression.
    """

    def extract_first(self, element: Any, default: Any = sentinel) -> Any:
        """
        Extract the first data or subelement from `extract` method call result.

        :param element: The target data node element.
        :param default: Default value when not found. Default: :data:`data_extractor.utils.sentinel`.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExtractError: Thrown by extractor extracting wrong data.
        """
        rv = self.extract(element)
        if not isinstance(rv, list):
            warnings.warn(
                f"{self!r} can't extract first item from result {rv!r}", UserWarning
            )
            return rv

        if not rv:
            if default is sentinel:
                from .exceptions import ExtractError

                raise ExtractError(self, element)

            return default

        return rv[0]


__all__ = ("AbstractExtractor", "ComplexExtractorMeta", "SimpleExtractorBase")
