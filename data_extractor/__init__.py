"""
:mod:`data_extractor`
=====================
Combine **XPath**, **CSS Selectors** and **JSONPath** for Web data extracting.
"""
# Local Folder
from .abc import (
    AbstractComplexExtractor,
    AbstractExtractors,
    AbstractSimpleExtractor,
    ComplexExtractorMeta,
)
from .exceptions import ExprError, ExtractError
from .item import Field, Item
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
    DummyMixin,
    LazyStr,
    create_dummy_extractor_cls,
    is_complex_extractor,
    is_dummy_extractor_cls,
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
    "DummyMixin",
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
    "TextCSSExtractor",
    "XPathExtractor",
    "create_dummy_extractor_cls",
    "is_complex_extractor",
    "is_dummy_extractor_cls",
    "is_extractor",
    "is_simple_extractor",
    "sentinel",
)
