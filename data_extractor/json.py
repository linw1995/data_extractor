# Standard Library
from typing import Any

# Third Party Library
import jsonpath_rw

# Local Folder
from .abc import AbstractExtractor


class JSONExtractor(AbstractExtractor):
    def extract(self, element: Any) -> Any:
        return [m.value for m in jsonpath_rw.parse(self.expr).find(element)]


__all__ = ("JSONExtractor",)
