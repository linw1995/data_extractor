# Standard Library
import importlib.util
import re

# Third Party Library
import pytest

# First Party Library
from data_extractor.exceptions import ExprError, ExtractError
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
)

need_cssselect = pytest.mark.skipif(
    importlib.util.find_spec("cssselect") is None,
    reason="Missing 'cssselect'",
)
need_lxml = pytest.mark.skipif(
    importlib.util.find_spec("lxml") is None, reason="Missing 'lxml'"
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
    try:
        # Third Party Library
        from lxml.html import fromstring
    except ImportError:
        pytest.skip("Missing 'lxml'")

    return fromstring(text)


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        pytest.param(TextCSSExtractor, "span.class_a", ["a"], marks=need_cssselect),
        pytest.param(TextCSSExtractor, "span.class_b", ["b"], marks=need_cssselect),
        pytest.param(TextCSSExtractor, "span", ["a", "b", "c"], marks=need_cssselect),
        pytest.param(TextCSSExtractor, "notexits", [], marks=need_cssselect),
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
        pytest.param(TextCSSExtractor, "span.class_a", "a", marks=need_cssselect),
        pytest.param(TextCSSExtractor, "span.class_b", "b", marks=need_cssselect),
        pytest.param(TextCSSExtractor, "span", "a", marks=need_cssselect),
        pytest.param(TextCSSExtractor, "notexits", "default", marks=need_cssselect),
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
    [
        pytest.param(TextCSSExtractor, "notexits", marks=need_cssselect),
        (XPathExtractor, "//notexists/text()"),
    ],
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


@need_cssselect
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


@need_cssselect
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


@need_cssselect
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


@need_lxml
@pytest.mark.parametrize("expr", ["///", "/text(", ""])
def test_invalid_xpath_expr(expr):
    with pytest.raises(ExprError) as catch:
        XPathExtractor(expr)

    exc = catch.value
    # Third Party Library
    from lxml.etree import XPathError

    assert isinstance(exc.exc, XPathError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


@pytest.mark.parametrize("expr", ["//ns:a"])
def test_invalid_xpath_expr_by_XPathEvalError_from_extract(element, expr):
    extractor = XPathExtractor(expr)
    with pytest.raises(ExprError) as catch:
        extractor.extract(element)

    exc = catch.value
    assert exc.extractor is extractor
    # Third Party Library
    from lxml.etree import XPathEvalError

    assert isinstance(exc.exc, XPathEvalError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


@need_cssselect
@pytest.mark.parametrize("expr", ["<", "a##", ""])
def test_invalid_css_selector_expr(element, expr):
    with pytest.raises(ExprError) as catch:
        CSSExtractor(expr)

    exc = catch.value
    # Third Party Library
    from cssselect.parser import SelectorError

    assert isinstance(exc.exc, SelectorError)
    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))


def test_xpath_result_not_list(element):
    extractor = XPathExtractor("normalize-space(//span)")
    assert extractor.extract(element) == ["a"]
    assert extractor.extract_first(element) == "a"
