# Standard Library
import json

# Third Party Library
import pytest

from jsonpath_rw.lexer import JsonPathLexerError

# First Party Library
from data_extractor.exceptions import ExprError, ExtractError
from data_extractor.json import JSONExtractor


@pytest.fixture(scope="module")
def text():
    return """
        {
            "foo": [
                {
                    "baz": 1
                },
                {
                    "baz": 2
                }
            ]
        }
    """


@pytest.fixture(scope="module")
def element(text):
    return json.loads(text)


@pytest.mark.parametrize(
    "expr,expect",
    [
        ("foo[*].baz", [1, 2]),
        ("foo.baz", []),
        ("foo[0].baz", [1]),
        ("foo[1].baz", [2]),
        ("foo[2].baz", []),
    ],
    ids=repr,
)
def test_extract(element, expr, expect):
    assert expect == JSONExtractor(expr).extract(element)


@pytest.mark.parametrize(
    "expr,expect",
    [
        ("foo[*].baz", 1),
        ("foo.baz", "default"),
        ("foo[0].baz", 1),
        ("foo[1].baz", 2),
        ("foo[2].baz", "default"),
    ],
    ids=repr,
)
def test_extract_first(element, expr, expect):
    assert expect == JSONExtractor(expr).extract_first(element, default="default")


@pytest.mark.parametrize("expr", ["foo.baz", "foo[2].baz"], ids=repr)
def test_extract_first_without_default(element, expr):
    extractor = JSONExtractor(expr)
    with pytest.raises(ExtractError) as catch:
        extractor.extract_first(element)

    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element


@pytest.mark.parametrize("expr", ["foo..", "a[]", ""], ids=repr)
def test_invalid_css_selector_expr(element, expr):
    extractor = JSONExtractor(expr)
    with pytest.raises(ExprError) as catch:
        extractor.extract(element)

    exc = catch.value
    assert exc.extractor is extractor
    assert isinstance(exc.exc, (JsonPathLexerError, Exception))
