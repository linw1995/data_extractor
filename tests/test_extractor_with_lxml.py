# Standard Library
import importlib.util

# Third Party Library
import pytest

# First Party Library
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
)


html = pytest.importorskip("lxml.html")
fromstring = html.fromstring


need_cssselect = pytest.mark.skipif(
    importlib.util.find_spec("cssselect") is None, reason="Missing 'cssselect'",
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
        pytest.param(
            AttrCSSExtractor,
            {"expr": "span.boo", "attr": "id"},
            html_element,
            "boo",
            marks=need_cssselect,
        ),
        pytest.param(
            CSSExtractor,
            {"expr": "span.boo"},
            html_element,
            target_element,
            marks=need_cssselect,
        ),
        pytest.param(
            TextCSSExtractor,
            {"expr": "span.boo"},
            html_element,
            "boo",
            marks=need_cssselect,
        ),
        (
            XPathExtractor,
            {"expr": "//*[@class='boo']/text()"},
            html_element,
            "boo",
        ),
    ],
)
def test_build_implicitly_by_xpath(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built


@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        pytest.param(
            AttrCSSExtractor,
            {"expr": "span.boo", "attr": "id"},
            html_element,
            "boo",
            marks=need_cssselect,
        ),
        pytest.param(
            CSSExtractor,
            {"expr": "span.boo"},
            html_element,
            target_element,
            marks=need_cssselect,
        ),
        pytest.param(
            TextCSSExtractor,
            {"expr": "span.boo"},
            html_element,
            "boo",
            marks=need_cssselect,
        ),
        (
            XPathExtractor,
            {"expr": "//*[@class='boo']/text()"},
            html_element,
            "boo",
        ),
    ],
)
def test_build_explicitly_by_xpath(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    extractor.build()
    assert extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built


@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        pytest.param(
            AttrCSSExtractor,
            {"expr": "span.boo", "attr": "id"},
            html_element,
            "boo",
            marks=need_cssselect,
        ),
        pytest.param(
            CSSExtractor,
            {"expr": "span.boo"},
            html_element,
            target_element,
            marks=need_cssselect,
        ),
        pytest.param(
            TextCSSExtractor,
            {"expr": "span.boo"},
            html_element,
            "boo",
            marks=need_cssselect,
        ),
        (
            XPathExtractor,
            {"expr": "//*[@class='boo']/text()"},
            html_element,
            "boo",
        ),
    ],
)
def test_modify_built_by_xpath(Extractor, kwargs, element, expect):
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
