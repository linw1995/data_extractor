# Standard Library
import json
import re

# Third Party Library
import pytest

# First Party Library
import data_extractor.json

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


@pytest.mark.usefixtures("json_extractor_backend")
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
    extractor = JSONExtractor(expr)
    assert expect == extractor.extract(element)


@pytest.mark.usefixtures("json_extractor_backend")
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
    extractor = JSONExtractor(expr)
    assert expect == extractor.extract_first(element, default="default")


@pytest.mark.usefixtures("json_extractor_backend")
@pytest.mark.parametrize("expr", ["foo.baz", "foo[2].baz"], ids=repr)
def test_extract_first_without_default(element, expr):
    extractor = JSONExtractor(expr)

    with pytest.raises(ExtractError) as catch:
        extractor.extract_first(element)

    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element


@pytest.mark.usefixtures("json_extractor_backend")
@pytest.mark.parametrize("expr", ["foo..", "a[]", ""], ids=repr)
def test_invalid_jsonpath_expr(element, expr):
    with pytest.raises(ExprError) as catch:
        JSONExtractor(expr)

    exc = catch.value

    if (
        data_extractor.json.json_extractor_backend
        is data_extractor.json.JSONPathExtractor
    ):
        # JSONExtractor implementated by 'jsonpath-extractor'
        # only raise SyntaxError
        assert isinstance(exc.exc, SyntaxError)
    else:
        # Third Party Library
        from jsonpath_rw.lexer import JsonPathLexerError

        assert isinstance(exc.exc, (JsonPathLexerError, Exception))

    assert re.match(r"ExprError with .+? raised by .+? extracting", str(exc))
