"""
===================================================
:mod:`json` -- Extractors for JSON data extracting.
===================================================
"""
# Standard Library
from typing import Any, Optional

# Third Party Library
import jsonpath_rw_ext

from jsonpath_rw import JSONPath
from jsonpath_rw.lexer import JsonPathLexerError

# Local Folder
from .abc import AbstractSimpleExtractor
from .exceptions import ExprError


class JSONExtractor(AbstractSimpleExtractor):
    """
    Use JSONPath expression for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    def __init__(self, expr: str) -> None:
        super().__init__(expr)
        self._jsonpath: Optional[JSONPath] = None

    def build(self) -> None:
        try:
            self._jsonpath = jsonpath_rw_ext.parse(self.expr)
            self.built = True
        except (JsonPathLexerError, Exception) as exc:
            # jsonpath_rw.parser.JsonPathParser.p_error raises exc of Exception type
            raise ExprError(extractor=self, exc=exc) from exc

    def extract(self, element: Any) -> Any:
        """
        Extract data from JSON data.

        :param element: Python object parsed from JSON text.
        :type element: Any

        :returns: Data.
        :rtype: Any
        """
        if not self.built:
            self.build()

        assert self._jsonpath is not None
        return [m.value for m in self._jsonpath.find(element)]


__all__ = ("JSONExtractor",)
