"""
:mod:`lxml` -- Extractors for XML or HTML data extracting.
==========================================================
"""
# Standard Library
from typing import List, Optional, Union

# Third Party Library
from cssselect import GenericTranslator
from cssselect.parser import SelectorError
from lxml.etree import XPath, XPathEvalError, XPathSyntaxError
from lxml.etree import _Element as Element

# Local Folder
from .abc import AbstractSimpleExtractor, BuildProperty
from .exceptions import ExprError


class CSSExtractor(AbstractSimpleExtractor):
    """
    Use CSS Selector for XML or HTML data subelements extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    """

    def __init__(self, expr: str):
        super().__init__(expr)
        self._extractor: Optional[XPathExtractor] = None

    def build(self) -> None:
        try:
            xpath_expr = GenericTranslator().css_to_xpath(self.expr)
        except SelectorError as exc:
            raise ExprError(extractor=self, exc=exc) from exc

        self._extractor = XPathExtractor(xpath_expr)
        self._extractor.build()
        self.built = True

    def extract(self, element: Element) -> List[Element]:
        """
        Extract subelements from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of :class:`data_extractor.lxml.Element` objects, \
            extracted result.
        :rtype: list
        """
        if not self.built:
            self.build()

        assert self._extractor is not None
        result = self._extractor.extract(element)
        assert not isinstance(result, str)
        return result


class TextCSSExtractor(CSSExtractor):
    """
    Use CSS Selector for XML or HTML data subelements' text extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    """

    def extract(self, element: Element) -> List[str]:
        """
        Extract subelements' text from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of str, extracted result.
        :rtype: list

        :raises ~data_extractor.exceptions.ExprError: CSS Selector Expression Error.
        """
        return [ele.text for ele in super().extract(element)]


class AttrCSSExtractor(CSSExtractor):
    """
    Use CSS Selector for XML or HTML data subelements' attribute value extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    :param attr: Target attribute name.
    :type attr: str
    """

    attr = BuildProperty()

    def __init__(self, expr: str, attr: str):
        super().__init__(expr)
        self.attr = attr

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"
        )

    def extract(self, element: Element) -> List[str]:
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
            for ele in super().extract(element)
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

    def __init__(self, expr: str):
        super().__init__(expr)
        self._find: Optional[XPath] = None

    def build(self) -> None:
        try:
            self._find = XPath(self.expr)
            self.built = True
        except XPathSyntaxError as exc:
            raise ExprError(extractor=self, exc=exc) from exc

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
        if not self.built:
            self.build()

        try:
            assert self._find is not None
            return self._find(element)
        except XPathEvalError as exc:
            raise ExprError(extractor=self, exc=exc) from exc


__all__ = (
    "AttrCSSExtractor",
    "CSSExtractor",
    "Element",
    "TextCSSExtractor",
    "XPathExtractor",
)
