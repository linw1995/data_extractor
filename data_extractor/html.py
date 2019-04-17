# Standard Library
from typing import List, Union

# Third Party Library
from lxml.etree import _Element as HTMLElement
from lxml.html import fromstring, tostring

# Local Folder
from .abc import AbstractExtractor


class CSSExtractor(AbstractExtractor):
    def extract(self, element: HTMLElement) -> List[HTMLElement]:
        return element.cssselect(self.expr)


class TextCSSExtractor(AbstractExtractor):
    def extract(self, element: HTMLElement) -> List[str]:
        return [ele.text for ele in CSSExtractor(self.expr).extract(element)]


class AttrCSSExtractor(AbstractExtractor):
    def __init__(self, expr: str, attr: str):
        super().__init__(expr)
        self.attr = attr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"

    def extract(self, root: HTMLElement) -> List[str]:
        return [
            ele.get(self.attr)
            for ele in CSSExtractor(self.expr).extract(root)
            if self.attr in ele.keys()
        ]


class XPathExtractor(AbstractExtractor):
    def extract(self, element: HTMLElement) -> Union[List["HTMLElement"], List[str]]:
        return element.xpath(self.expr)


__all__ = (
    "AttrCSSExtractor",
    "CSSExtractor",
    "HTMLElement",
    "TextCSSExtractor",
    "XPathExtractor",
    "fromstring",
    "tostring",
)
