# Standard Library
import re

# Third Party Library
import pytest

from cssselect.parser import SelectorError
from lxml.etree import XPathError, XPathEvalError

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
def test_extract(element, Extractor, expr, expect, build_first):
    extractor = Extractor(expr)
    assert not extractor.built
    if build_first:
        extractor.build()
        assert extractor.built

    assert expect == extractor.extract(element)
    assert extractor.built


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
def test_extract_first(element, Extractor, expr, expect, build_first):
    extractor = Extractor(expr)
    assert not extractor.built
    if build_first:
        extractor.build()
        assert extractor.built

    assert expect == extractor.extract_first(element, default="default")
    assert extractor.built


@pytest.mark.parametrize(
    "Extractor,expr",
    [(TextCSSExtractor, "notexits"), (XPathExtractor, "//notexists/text()")],
    ids=repr,
)
def test_extract_first_without_default(element, Extractor, expr, build_first):
    extractor = Extractor(expr)
    assert not extractor.built
    if build_first:
        extractor.build()
        assert extractor.built

    with pytest.raises(ExtractError) as catch:
        extractor.extract_first(element)

    assert extractor.built
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
def test_attr_css_extract(element, expr, attr, expect, build_first):
    extractor = AttrCSSExtractor(expr=expr, attr=attr)
    assert not extractor.built
    if build_first:
        extractor.build()
        assert extractor.built

    assert expect == extractor.extract(element)
    assert extractor.built


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
def test_attr_css_extract_first(element, expr, attr, expect, build_first):
    extractor = AttrCSSExtractor(expr=expr, attr=attr)
    assert not extractor.built
    if build_first:
        extractor.build()
        assert extractor.built

    assert expect == extractor.extract_first(element, default="default")
    assert extractor.built


@pytest.mark.parametrize(
    "expr,attr", [("span", "notexists"), ("notexists", "class")], ids=repr
)
def test_attr_css_extract_first_without_default(
    element, expr, attr, build_first
):
    extractor = AttrCSSExtractor(expr=expr, attr=attr)
    assert not extractor.built
    if build_first:
        extractor.build()
        assert extractor.built

    with pytest.raises(ExtractError) as catch:
        extractor.extract_first(element)

    assert extractor.built
    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element


@pytest.mark.parametrize("expr", ["///", "/text(", ""])
def test_invalid_xpath_expr_by_build(expr):
    extractor = XPathExtractor(expr)
    assert not extractor.built
    with pytest.raises(ExprError) as catch:
        extractor.build()

    assert not extractor.built
    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, XPathError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


@pytest.mark.parametrize("expr", ["///", "/text(", "", "\\", "//*[1.1.1]"])
def test_invalid_xpath_expr_by_extract(element, expr):
    extractor = XPathExtractor(expr)
    assert not extractor.built
    with pytest.raises(ExprError) as catch:
        extractor.extract(element)

    assert not extractor.built
    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, XPathError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


@pytest.mark.parametrize("expr", ["//ns:a"])
def test_invalid_xpath_expr_by_XPathEvalError_from_extract(element, expr):
    extractor = XPathExtractor(expr)
    assert not extractor.built

    extractor.build()
    assert extractor.built

    with pytest.raises(ExprError) as catch:
        extractor.extract(element)

    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, XPathEvalError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


@pytest.mark.parametrize("by", ["build", "extract"], ids=lambda x: f"by_{x}")
@pytest.mark.parametrize("expr", ["<", "a##", ""])
def test_invalid_css_selector_expr(element, expr, by):
    extractor = CSSExtractor(expr)
    assert not extractor.built
    with pytest.raises(ExprError) as catch:
        if by == "build":
            extractor.build()
        else:
            extractor.extract(element)

    assert not extractor.built
    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, SelectorError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


def test_xpath_result_not_list(element):
    extractor = XPathExtractor("normalize-space(//span)")

    assert extractor.extract(element) == "a"

    with pytest.warns(UserWarning):
        extractor.extract_first(element) == "a"
