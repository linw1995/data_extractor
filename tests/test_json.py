# Standard Library
import json

# Third Party Library
import pytest

# Dsipder Module
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
)
def test_extract_first(element, expr, expect):
    assert expect == JSONExtractor(expr).extract_first(element, default="default")


@pytest.mark.parametrize("expr", [("foo.baz",), ("foo[2].baz",)])
def test_extract_first_without_default(element, expr):
    with pytest.raises(ValueError):
        JSONExtractor(expr).extract_first(element)
