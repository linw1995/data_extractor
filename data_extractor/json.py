"""
:mod:`json` -- Extractors for JSON data extracting.
===================================================
"""
# Standard Library
from typing import Any

# Third Party Library
import jsonpath_rw

from jsonpath_rw.lexer import JsonPathLexerError

# Local Folder
from .abc import SimpleExtractorBase
from .exceptions import ExprError


class JSONExtractor(SimpleExtractorBase):
    """
    Use JSONPath expression for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    """

    def extract(self, element: Any) -> Any:
        """
        Extract data from JSON data.

        :param element: Python object parsed from JSON text.

        :returns: Data.

        :raises data_extractor.exceptions.ExprError: JSONPath Expression Error.
        """
        try:
            finder = jsonpath_rw.parse(self.expr)
        except (JsonPathLexerError, Exception) as exc:
            raise ExprError(extractor=self, exc=exc)

        return [m.value for m in finder.find(element)]


__all__ = ("JSONExtractor",)
