"""
:mod:`data_extractor`
=====================
Combine **XPath**, **CSS Selectors** and **JSONPath** for Web data extracting.
"""

# Local Folder
from .core import (
    AbstractComplexExtractor,
    AbstractExtractors,
    AbstractSimpleExtractor,
    ComplexExtractorMeta,
)
from .exceptions import ExprError, ExtractError
from .item import RV, Convertor, Field, Item
from .json import (
    JSONExtractor,
    JSONPathExtractor,
    JSONPathRWExtExtractor,
    JSONPathRWExtractor,
)
from .lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    Element,
    TextCSSExtractor,
    XPathExtractor,
)
from .utils import (
    LazyStr,
    is_complex_extractor,
    is_extractor,
    is_simple_extractor,
    sentinel,
)

__all__ = (
    "AbstractComplexExtractor",
    "AbstractExtractors",
    "AbstractSimpleExtractor",
    "AttrCSSExtractor",
    "CSSExtractor",
    "ComplexExtractorMeta",
    "Convertor",
    "Element",
    "ExprError",
    "ExtractError",
    "Field",
    "Item",
    "JSONExtractor",
    "JSONPathExtractor",
    "JSONPathRWExtExtractor",
    "JSONPathRWExtractor",
    "LazyStr",
    "RV",
    "TextCSSExtractor",
    "XPathExtractor",
    "is_complex_extractor",
    "is_extractor",
    "is_simple_extractor",
    "sentinel",
)
