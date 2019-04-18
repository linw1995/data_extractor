# Standard Library
from typing import List, Union

# Third Party Library
from lxml.etree import _Element as Element

# Local Folder
from .abc import AbstractExtractor


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
        return element.xpath(self.expr)


__all__ = (
    "AttrCSSExtractor",
    "CSSExtractor",
    "Element",
    "TextCSSExtractor",
    "XPathExtractor",
)
