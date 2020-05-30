# Third Party Library
import pytest

# First Party Library
from data_extractor.item import Field, Item
from data_extractor.json import (
    JSONPathExtractor,
    JSONPathRWExtExtractor,
    JSONPathRWExtractor,
)
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
)
from data_extractor.utils import (
    LazyStr,
    is_complex_extractor,
    is_dummy_extractor_cls,
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
        AttrCSSExtractor(expr="div.class", attr="id")
        if not is_dummy_extractor_cls(AttrCSSExtractor)
        else pytest.param("Missing 'cssselect'", marks=pytest.mark.skip()),
        CSSExtractor(expr="div.class")
        if not is_dummy_extractor_cls(CSSExtractor)
        else pytest.param("Missing 'cssselect'", marks=pytest.mark.skip()),
        JSONPathExtractor(expr="boo")
        if not is_dummy_extractor_cls(JSONPathExtractor)
        else pytest.param(
            "Missing 'jsonpath-extractor'", marks=pytest.mark.skip()
        ),
        JSONPathRWExtractor(expr="boo")
        if not is_dummy_extractor_cls(JSONPathRWExtractor)
        else pytest.param("Missing 'jsonpath-rw'", marks=pytest.mark.skip()),
        JSONPathRWExtExtractor(expr="boo")
        if not is_dummy_extractor_cls(JSONPathRWExtExtractor)
        else pytest.param(
            "Missing 'jsonpath-rw-ext'", marks=pytest.mark.skip()
        ),
        TextCSSExtractor(expr="div.class")
        if not is_dummy_extractor_cls(TextCSSExtractor)
        else pytest.param("Missing 'cssselect'", marks=pytest.mark.skip()),
        XPathExtractor(expr="//div")
        if not is_dummy_extractor_cls(XPathExtractor)
        else pytest.param("Missing 'lxml'", marks=pytest.mark.skip()),
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


def test_create_dummy_extractor():
    from data_extractor.utils import create_dummy_extractor_cls

    DummyExtractor = create_dummy_extractor_cls(
        "DummyExtractor", "optional_dependency"
    )
    assert is_dummy_extractor_cls(DummyExtractor)

    with pytest.raises(RuntimeError) as catched:
        DummyExtractor()

    assert "optional_dependency" in str(catched.value)
