# Standard Library
from typing import List, Union

# Third Party Library
from lxml.etree import XPathEvalError
from lxml.etree import _Element as Element

# Local Folder
from .abc import AbstractExtractor
from .exceptions import ExprError


class CSSExtractor(AbstractExtractor):
    def extract(self, element: Element) -> List[Element]:
        return element.cssselect(self.expr)


class TextCSSExtractor(AbstractExtractor):
    def extract(self, element: Element) -> List[str]:
        return [ele.text for ele in CSSExtractor(self.expr).extract(element)]


class AttrCSSExtractor(AbstractExtractor):
    def __init__(self, expr: str, attr: str):
        super().__init__(expr)
        self.attr = attr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"

    def extract(self, root: Element) -> List[str]:
        return [
            ele.get(self.attr)
            for ele in CSSExtractor(self.expr).extract(root)
            if self.attr in ele.keys()
        ]


class XPathExtractor(AbstractExtractor):
    def extract(self, element: Element) -> Union[List["Element"], List[str]]:
        try:
            return element.xpath(self.expr)
        except XPathEvalError as exc:
            raise ExprError(extractor=self, exc=exc)


__all__ = (
    "AttrCSSExtractor",
    "CSSExtractor",
    "Element",
    "TextCSSExtractor",
    "XPathExtractor",
)
