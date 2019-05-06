"""
:mod:`lxml` -- Extractors for XML or HTML data extracting.
==========================================================
"""
# Standard Library
from typing import List, Union

# Third Party Library
from cssselect.parser import SelectorSyntaxError
from lxml.etree import XPathEvalError
from lxml.etree import _Element as Element

# Local Folder
from .abc import SimpleExtractorBase
from .exceptions import ExprError


class CSSExtractor(SimpleExtractorBase):
    """
    Use CSS Selector for XML or HTML data subelements extracting.

    Before extracting, should parse the XML or HTML text into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    """

    def extract(self, element: Element) -> List[Element]:
        """
        Extract subelements from XML or HTML data.

        :param element: :class:`data_extractor.lxml.Element` object.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        try:
            return element.cssselect(self.expr)
        except SelectorSyntaxError as exc:
            raise ExprError(extractor=self, exc=exc)


class TextCSSExtractor(SimpleExtractorBase):
    """
    Use CSS Selector for XML or HTML data subelements' text extracting.

    Before extracting, should parse the XML or HTML text into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    """

    def __init__(self, expr: str):
        super().__init__(expr)
        self.extractor = CSSExtractor(self.expr)

    def extract(self, element: Element) -> List[str]:
        """
        Extract subelements' text from XML or HTML data.

        :param element: :class:`data_extractor.lxml.Element` object.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        return [ele.text for ele in self.extractor.extract(element)]


class AttrCSSExtractor(SimpleExtractorBase):
    """
    Use CSS Selector for XML or HTML data subelements' attribute value extracting.

    Before extracting, should parse the XML or HTML text into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :param attr: Target attribute name.
    """

    def __init__(self, expr: str, attr: str):
        super().__init__(expr)
        self.extractor = CSSExtractor(self.expr)
        self.attr = attr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"

    def extract(self, root: Element) -> List[str]:
        """
        Extract subelements' attribute value from XML or HTML data.

        :param element: :class:`data_extractor.lxml.Element` object.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        return [
            ele.get(self.attr)
            for ele in self.extractor.extract(root)
            if self.attr in ele.keys()
        ]


class XPathExtractor(SimpleExtractorBase):
    """
    Use XPath for XML or HTML data extracting.

    Before extracting, should parse the XML or HTML text into :class:`data_extractor.lxml.Element` object.

    :param expr: XPath Expression.
    """

    def extract(self, element: Element) -> Union[List[Element], List[str]]:
        """
        Extract subelements or data from XML or HTML data.

        :param element: :class:`data_extractor.lxml.Element` object.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExprError: XPath Expression Error.
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
