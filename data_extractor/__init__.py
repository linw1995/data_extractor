"""
:mod:`data_extractor`
=====================
Combine **XPath**, **CSS Selector** and **JSONPath** for Web data extracting.
"""
__version__ = "0.2.1"

# Local Folder
from .abc import AbstractExtractor, ComplexExtractorMeta, SimpleExtractorBase
from .exceptions import ExprError, ExtractError
from .item import Field, Item
from .json import JSONExtractor
from .lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    Element,
    TextCSSExtractor,
    XPathExtractor,
)
from .utils import LazyStr, sentinel


__all__ = (
    "AbstractExtractor",
    "AttrCSSExtractor",
    "CSSExtractor",
    "ComplexExtractorMeta",
    "Element",
    "ExprError",
    "ExtractError",
    "Field",
    "Item",
    "JSONExtractor",
    "LazyStr",
    "SimpleExtractorBase",
    "TextCSSExtractor",
    "XPathExtractor",
    "sentinel",
)
