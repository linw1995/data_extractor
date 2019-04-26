# Third Party Library
import pytest

from cssselect.parser import SelectorSyntaxError
from lxml.etree import XPathEvalError

# First Party Library
from data_extractor.exceptions import ExprError, ExtractError
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
)


@pytest.fixture(scope="module")
def text():
    return """
        <html>
            <ul>
                <li>
                    <span class='class_a'>a</span>
                    <i>i text 1</i>
                    <b>b text 1</b>
                </li>
                <li>
                    <span class='class_b'>b</span>
                    <i>i text 2</i>
                    <b>b text 2</b>
                </li>
                <li>
                    <span>c</span>
                    <i>i text 3</i>
                    <b>b text 3</b>
                </li>
            </ul>
        </html>
    """


@pytest.fixture(scope="module")
def element(text):
    from lxml.html import fromstring

    return fromstring(text)


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (TextCSSExtractor, "span.class_a", ["a"]),
        (TextCSSExtractor, "span.class_b", ["b"]),
        (TextCSSExtractor, "span", ["a", "b", "c"]),
        (TextCSSExtractor, "notexits", []),
        (XPathExtractor, "//span[@class='class_a']/text()", ["a"]),
        (XPathExtractor, "//span[@class='class_b']/text()", ["b"]),
        (XPathExtractor, "//span[@class]/text()", ["a", "b"]),
        (XPathExtractor, "//span/@class", ["class_a", "class_b"]),
        (XPathExtractor, "//notexists/text()", []),
    ],
    ids=repr,
)
def test_extract(element, Extractor, expr, expect):
    extractor = Extractor(expr)
    assert expect == extractor.extract(element)


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (TextCSSExtractor, "span.class_a", "a"),
        (TextCSSExtractor, "span.class_b", "b"),
        (TextCSSExtractor, "span", "a"),
        (TextCSSExtractor, "notexits", "default"),
        (XPathExtractor, "//span[@class='class_a']/text()", "a"),
        (XPathExtractor, "//span[@class='class_b']/text()", "b"),
        (XPathExtractor, "//span[@class]/text()", "a"),
        (XPathExtractor, "//span/@class", "class_a"),
        (XPathExtractor, "//notexists/text()", "default"),
    ],
    ids=repr,
)
def test_extract_first(element, Extractor, expr, expect):
    extractor = Extractor(expr)
    assert expect == extractor.extract_first(element, default="default")


@pytest.mark.parametrize(
    "Extractor,expr",
    [(TextCSSExtractor, "notexits"), (XPathExtractor, "//notexists/text()")],
    ids=repr,
)
def test_extract_first_without_default(element, Extractor, expr):
    extractor = Extractor(expr)
    with pytest.raises(ExtractError) as catch:
        extractor.extract_first(element)

    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element


@pytest.mark.parametrize(
    "expr,attr,expect",
    [
        ("span.class_a", "class", ["class_a"]),
        ("span.class_b", "class", ["class_b"]),
        ("span", "class", ["class_a", "class_b"]),
        ("span", "notexists", []),
        ("notexists", "class", []),
    ],
    ids=repr,
)
def test_attr_css_extract(element, expr, attr, expect):
    extractor = AttrCSSExtractor(expr=expr, attr=attr)
    assert expect == extractor.extract(element)


@pytest.mark.parametrize(
    "expr,attr,expect",
    [
        ("span.class_a", "class", "class_a"),
        ("span.class_b", "class", "class_b"),
        ("span", "class", "class_a"),
        ("span", "notexists", "default"),
        ("notexists", "class", "default"),
    ],
    ids=repr,
)
def test_attr_css_extract_first(element, expr, attr, expect):
    extractor = AttrCSSExtractor(expr=expr, attr=attr)
    assert expect == extractor.extract_first(element, default="default")


@pytest.mark.parametrize(
    "expr,attr", [("span", "notexists"), ("notexists", "class")], ids=repr
)
def test_attr_css_extract_first_without_default(element, expr, attr):
    extractor = AttrCSSExtractor(expr=expr, attr=attr)
    with pytest.raises(ExtractError) as catch:
        extractor.extract_first(element)

    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element


@pytest.mark.parametrize("expr", ["///", "/text(", ""])
def test_invalid_xpath_expr(element, expr):
    extractor = XPathExtractor(expr)
    with pytest.raises(ExprError) as catch:
        extractor.extract(element)

    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, XPathEvalError)


@pytest.mark.parametrize("expr", ["<", "a##", ""])
def test_invalid_css_selector_expr(element, expr):
    extractor = CSSExtractor(expr)
    with pytest.raises(ExprError) as catch:
        extractor.extract(element)

    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, SelectorSyntaxError)


def test_xpath_result_not_list(element):
    extractor = XPathExtractor("normalize-space(//span)")

    assert extractor.extract(element) == "a"

    with pytest.warns(UserWarning):
        extractor.extract_first(element) == "a"
