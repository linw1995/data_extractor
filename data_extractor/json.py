"""
Extractors for JSON data extracting.
"""
# Standard Library
from typing import Any

# Third Party Library
import jsonpath_rw

# Local Folder
from .abc import AbstractExtractor


class JSONExtractor(AbstractExtractor):
    """
    Use JSONPath expression for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.
    """

    def extract(self, element: Any) -> Any:
        """
        Extract data from JSON data.
        """
        return [m.value for m in jsonpath_rw.parse(self.expr).find(element)]


__all__ = ("JSONExtractor",)
