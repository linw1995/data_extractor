"""
:mod:`lxml` -- Extractors for XML or HTML data extracting.
==========================================================
"""

# Standard Library
from typing import List, Union

# Local Folder
from .core import AbstractSimpleExtractor
from .exceptions import ExprError
from .utils import Property, _missing_dependency

try:
    # Third Party Library
    from lxml.etree import XPath, XPathSyntaxError
    from lxml.etree import _Element as Element

    _missing_lxml = False
except ImportError:
    _missing_lxml = True

    Element = None  # TODO: Find a way to get rid of this. See PEP 562


class XPathExtractor(AbstractSimpleExtractor):
    """
    Use XPath for XML or HTML data extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: XPath Expression.
    :type exprt: str
    """

    _find = Property["XPath"]()

    def __init__(self, expr: str):
        super().__init__(expr)

        if _missing_lxml:
            _missing_dependency("lxml")

        try:
            self._find = XPath(self.expr)
        except XPathSyntaxError as exc:
            raise ExprError(extractor=self, exc=exc) from exc

    def extract(self, element: Element) -> Union[List[Element], List[str]]:
        """
        Extract subelements or data from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of :class:`data_extractor.lxml.Element` objects, \
            List of str, or str.
        :rtype: list

        :raises data_extractor.exceptions.ExprError: XPath Expression Error.
        """
        # Third Party Library
        from lxml.etree import XPathEvalError

        try:
            rv = self._find(element)
            if not isinstance(rv, list):
                return [rv]
            else:
                return rv
        except XPathEvalError as exc:
            raise ExprError(extractor=self, exc=exc) from exc


try:
    # Third Party Library
    import cssselect

    del cssselect
    _missing_cssselect = False
except ImportError:
    _missing_cssselect = True


class CSSExtractor(AbstractSimpleExtractor):
    """
    Use CSS Selector for XML or HTML data subelements extracting.

    Before extracting, should parse the XML or HTML text \
        into :class:`data_extractor.lxml.Element` object.

    :param expr: CSS Selector Expression.
    :type expr: str
    """

    _extractor = Property[XPathExtractor]()

    def __init__(self, expr: str):
        super().__init__(expr)

        if _missing_cssselect:
            _missing_dependency("cssselect")

        # Third Party Library
        from cssselect import GenericTranslator
        from cssselect.parser import SelectorError

        try:
            xpath_expr = GenericTranslator().css_to_xpath(self.expr)
        except SelectorError as exc:
            raise ExprError(extractor=self, exc=exc) from exc

        self._extractor = XPathExtractor(xpath_expr)

    def extract(self, element: Element) -> List[Element]:
        """
        Extract subelements from XML or HTML data.

        :param element: Target.
        :type element: :class:`data_extractor.lxml.Element`

        :returns: List of :class:`data_extractor.lxml.Element` objects, \
            extracted result.
        :rtype: list
        """
        return self._extractor.extract(element)


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

    attr = Property[str]()

    def __init__(self, expr: str, attr: str):
        super().__init__(expr)
        self.attr = attr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(expr={self.expr!r}, attr={self.attr!r})"

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


__all__ = (
    "AttrCSSExtractor",
    "CSSExtractor",
    "Element",
    "TextCSSExtractor",
    "XPathExtractor",
)
