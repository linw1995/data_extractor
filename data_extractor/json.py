"""
:mod:`json` -- Extractors for JSON data extracting.
===================================================
"""
# Standard Library
from typing import Any

# Third Party Library
import jsonpath_rw_ext

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

    def extract(self, element: Any) -> Any:
        """
        Extract data from JSON data.

        :param element: Python object parsed from JSON text.
        :type element: Any

        :returns: Data.
        :rtype: Any

        :raises ~data_extractor.exceptions.ExprError: JSONPath Expression Error.
        """
        try:
            finder = jsonpath_rw_ext.parse(self.expr)
        except (JsonPathLexerError, Exception) as exc:
            # jsonpath_rw.parser.JsonPathParser.p_error raises exc of Exception type
            raise ExprError(extractor=self, exc=exc) from exc

        return [m.value for m in finder.find(element)]


__all__ = ("JSONExtractor",)
