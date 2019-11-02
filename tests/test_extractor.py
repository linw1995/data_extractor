# Third Party Library
import pytest

from lxml.html import fromstring

# First Party Library
from data_extractor.json import JSONExtractor
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
)


html_element = fromstring(
    """
    <div>
        <span class='bar' id='bar'>bar</span>
        <span class='boo' id='boo'>boo</span>
    </div>
    """
)
target_element = html_element[1]


@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        (JSONExtractor, {"expr": "boo"}, {"boo": "boo"}, "boo"),
        (
            AttrCSSExtractor,
            {"expr": "span.boo", "attr": "id"},
            html_element,
            "boo",
        ),
        (CSSExtractor, {"expr": "span.boo"}, html_element, target_element),
        (TextCSSExtractor, {"expr": "span.boo"}, html_element, "boo"),
        (
            XPathExtractor,
            {"expr": "//*[@class='boo']/text()"},
            html_element,
            "boo",
        ),
    ],
)
def test_build_implicitly(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built


@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        (JSONExtractor, {"expr": "boo"}, {"boo": "boo"}, "boo"),
        (
            AttrCSSExtractor,
            {"expr": "span.boo", "attr": "id"},
            html_element,
            "boo",
        ),
        (CSSExtractor, {"expr": "span.boo"}, html_element, target_element),
        (TextCSSExtractor, {"expr": "span.boo"}, html_element, "boo"),
        (
            XPathExtractor,
            {"expr": "//*[@class='boo']/text()"},
            html_element,
            "boo",
        ),
    ],
)
def test_build_explicitly(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    extractor.build()
    assert extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built


@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        (JSONExtractor, {"expr": "boo"}, {"boo": "boo"}, "boo"),
        (
            AttrCSSExtractor,
            {"expr": "span.boo", "attr": "id"},
            html_element,
            "boo",
        ),
        (CSSExtractor, {"expr": "span.boo"}, html_element, target_element),
        (TextCSSExtractor, {"expr": "span.boo"}, html_element, "boo"),
        (
            XPathExtractor,
            {"expr": "//*[@class='boo']/text()"},
            html_element,
            "boo",
        ),
    ],
)
def test_modify_built(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    extractor.build()
    assert extractor.built

    extractor.expr = kwargs["expr"]
    assert not extractor.built

    extractor.build()
    assert extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built
