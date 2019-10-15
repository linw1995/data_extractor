# Third Party Library
import pytest

# First Party Library
from data_extractor.item import Field, Item
from data_extractor.json import JSONExtractor
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
)
from data_extractor.utils import (
    LazyStr,
    is_complex_extractor,
    is_extractor,
    is_simple_extractor,
)


def test_lazy_str():
    string = ""

    def func():
        nonlocal string
        return string

    ls = LazyStr(func=func)
    assert str(ls) == ""

    string = "abc"
    assert str(ls) == "abc"


@pytest.fixture(params=[Field(), Item()], ids=repr)
def complex_extractor(request):
    return request.param


@pytest.fixture(
    params=[
        AttrCSSExtractor(expr="div.class", attr="id"),
        CSSExtractor(expr="div.class"),
        JSONExtractor(expr="boo"),
        TextCSSExtractor(expr="div.class"),
        XPathExtractor(expr="//div"),
    ],
    ids=repr,
)
def simple_extractor(request):
    return request.param


def test_complex_extractor_is_extractor(complex_extractor):
    assert is_extractor(complex_extractor)


def test_simple_extractor_is_extractor(simple_extractor):
    assert is_extractor(simple_extractor)


def test_is_complex_extractor(complex_extractor):
    assert is_complex_extractor(complex_extractor)


def test_is_not_complex_extractor(simple_extractor):
    assert not is_complex_extractor(simple_extractor)


def test_is_simple_extractor(simple_extractor):
    assert is_simple_extractor(simple_extractor)


def test_is_not_simple_extractor(complex_extractor):
    assert not is_simple_extractor(complex_extractor)
