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
from .abc import AbstractSimpleExtractor
from .exceptions import ExprError


class CSSExtractor(AbstractSimpleExtractor):
    """
    Use CSS Selector for XML or HTML data subelements extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    """

    def extract(self, element: Element) -> List[Element]:
        """
        Extract subelements from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of :class:`data_extractor.lxml.Element` objects, \
            extracted result.
        :rtype: list

        :raises ~data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        try:
            return element.cssselect(self.expr)
        except SelectorSyntaxError as exc:
            raise ExprError(extractor=self, exc=exc) from exc


class TextCSSExtractor(AbstractSimpleExtractor):
    """
    Use CSS Selector for XML or HTML data subelements' text extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    """

    def __init__(self, expr: str):
        super().__init__(expr)
        self.extractor = CSSExtractor(self.expr)

    def extract(self, element: Element) -> List[str]:
        """
        Extract subelements' text from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of str, extracted result.
        :rtype: list

        :raises ~data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        return [ele.text for ele in self.extractor.extract(element)]


class AttrCSSExtractor(AbstractSimpleExtractor):
    """
    Use CSS Selector for XML or HTML data subelements' attribute value extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    :param attr: Target attribute name.
    :type attr: str
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

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of str, extracted result.
        :rtype: list

        :raises ~data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        return [
            ele.get(self.attr)
            for ele in self.extractor.extract(root)
            if self.attr in ele.keys()
        ]


class XPathExtractor(AbstractSimpleExtractor):
    """
    Use XPath for XML or HTML data extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: XPath Expression.
    :type exprt: str
    """

    def extract(self, element: Element) -> Union[List[Element], List[str], str]:
        """
        Extract subelements or data from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of :class:`data_extractor.lxml.Element` objects, \
            List of str, or str.
        :rtype: list, str

        :raises data_extractor.exceptions.ExprError: XPath Expression Error.
        """
        try:
            return element.xpath(self.expr)
        except XPathEvalError as exc:
            raise ExprError(extractor=self, exc=exc) from exc


__all__ = (
    "AttrCSSExtractor",
    "CSSExtractor",
    "Element",
    "TextCSSExtractor",
    "XPathExtractor",
)
