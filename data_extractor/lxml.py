"""
Extractors for XML or HTML data extracting.
"""
# Standard Library
from typing import List, Union

# Third Party Library
from lxml.etree import XPathEvalError
from lxml.etree import _Element as Element

# Local Folder
from .abc import AbstractExtractor
from .exceptions import ExprError


class CSSExtractor(AbstractExtractor):
    """
    Use CSS Selector for XML or HTML data subelements extracting.

    Before extracting, should parse the XML or HTML text into `ELement` object.
    """

    def extract(self, element: Element) -> List[Element]:
        """
        Extract subelements from XML or HTML data.
        """
        return element.cssselect(self.expr)


class TextCSSExtractor(AbstractExtractor):
    """
    Use CSS Selector for XML or HTML data subelements' text extracting.

    Before extracting, should parse the XML or HTML text into `ELement` object.
    """

    def extract(self, element: Element) -> List[str]:
        """
        Extract subelements' text from XML or HTML data.
        """
        return [ele.text for ele in CSSExtractor(self.expr).extract(element)]


class AttrCSSExtractor(AbstractExtractor):
    """
    Use CSS Selector for XML or HTML data subelements' attribute value extracting.

    Before extracting, should parse the XML or HTML text into `ELement` object.
    """

    def __init__(self, expr: str, attr: str):
        super().__init__(expr)
        self.attr = attr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"

    def extract(self, root: Element) -> List[str]:
        """
        Extract subelements' attribute value from XML or HTML data.
        """
        return [
            ele.get(self.attr)
            for ele in CSSExtractor(self.expr).extract(root)
            if self.attr in ele.keys()
        ]


class XPathExtractor(AbstractExtractor):
    """
    Use XPath for XML or HTML data extracting.

    Before extracting, should parse the XML or HTML text into `ELement` object.
    """

    def extract(self, element: Element) -> Union[List["Element"], List[str]]:
        """
        Extract subelements or data from XML or HTML data.
        """
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
