# Third Party Library
# Standard Library
import importlib.util
import sys

# Third Party Library
import pytest

# First Party Library
from data_extractor.core import AbstractSimpleExtractor
from data_extractor.item import Field, Item
from data_extractor.json import (
    JSONPathExtractor,
    JSONPathRWExtExtractor,
    JSONPathRWExtractor,
    _missing_jsonpath,
    _missing_jsonpath_rw,
    _missing_jsonpath_rw_ext,
)
from data_extractor.lxml import (
    AttrCSSExtractor,
    CSSExtractor,
    TextCSSExtractor,
    XPathExtractor,
    _missing_cssselect,
    _missing_lxml,
)
from data_extractor.utils import (
    LazyStr,
    Property,
    getframe,
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
        (
            AttrCSSExtractor(expr="div.class", attr="id")
            if not _missing_cssselect
            else pytest.param("Missing 'cssselect'", marks=pytest.mark.skip())
        ),
        (
            CSSExtractor(expr="div.class")
            if not _missing_cssselect
            else pytest.param("Missing 'cssselect'", marks=pytest.mark.skip())
        ),
        (
            JSONPathExtractor(expr="boo")
            if not _missing_jsonpath
            else pytest.param("Missing 'jsonpath-extractor'", marks=pytest.mark.skip())
        ),
        (
            JSONPathRWExtractor(expr="boo")
            if not _missing_jsonpath_rw
            else pytest.param("Missing 'jsonpath-rw'", marks=pytest.mark.skip())
        ),
        (
            JSONPathRWExtExtractor(expr="boo")
            if not _missing_jsonpath_rw_ext
            else pytest.param("Missing 'jsonpath-rw-ext'", marks=pytest.mark.skip())
        ),
        (
            TextCSSExtractor(expr="div.class")
            if not _missing_cssselect
            else pytest.param("Missing 'cssselect'", marks=pytest.mark.skip())
        ),
        (
            XPathExtractor(expr="//div")
            if not _missing_lxml
            else pytest.param("Missing 'lxml'", marks=pytest.mark.skip())
        ),
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


@pytest.mark.skipif(
    importlib.util.find_spec("cssselect") is not None,
    reason="'cssselect' installed",
)
def test_missing_cssselect():
    with pytest.raises(RuntimeError) as catch:
        CSSExtractor("a>b")

    assert "cssselect" in str(catch.value)

    with pytest.raises(RuntimeError) as catch:
        AttrCSSExtractor("a>b", "href")

    assert "cssselect" in str(catch.value)

    with pytest.raises(RuntimeError) as catch:
        TextCSSExtractor("a>b")

    assert "cssselect" in str(catch.value)


@pytest.mark.skipif(
    importlib.util.find_spec("lxml") is not None, reason="'lxml' installed"
)
def test_missing_lxml():
    with pytest.raises(RuntimeError) as catch:
        XPathExtractor("//boo")

    assert "lxml" in str(catch.value)


@pytest.mark.skipif(
    importlib.util.find_spec("jsonpath") is not None,
    reason="'jsonpath-extractor' installed",
)
def test_missing_jsonpath_extractor():
    with pytest.raises(RuntimeError) as catch:
        JSONPathExtractor("boo")

    assert "jsonpath-extractor" in str(catch.value)


@pytest.mark.skipif(
    importlib.util.find_spec("jsonpath_rw") is not None,
    reason="'jsonpath-rw' installed",
)
def test_missing_jsonpath_rw():
    with pytest.raises(RuntimeError) as catch:
        JSONPathRWExtractor("boo")

    assert "jsonpath-rw" in str(catch.value)

    with pytest.raises(RuntimeError) as catch:
        JSONPathRWExtExtractor("boo")

    assert "jsonpath-rw" in str(catch.value)


@pytest.mark.skipif(
    not (
        importlib.util.find_spec("jsonpath_rw_ext") is None
        and importlib.util.find_spec("jsonpath_rw") is not None
    ),
    reason="'jsonpath-rw-ext' installed or 'jsonpath-rw' uninstalled",
)
def test_missing_jsonpath_rw_ext():
    with pytest.raises(RuntimeError) as catch:
        JSONPathRWExtExtractor("boo")

    assert "jsonpath-rw-ext" in str(catch.value)


def test_getframe_value_error():
    with pytest.raises(ValueError):
        getframe(sys.getrecursionlimit() + 1)


def test_property_accessing_error():
    class Bar(AbstractSimpleExtractor):
        unset_attribute = Property[None]()

        def extract(self, element):
            return super().extract(element)

    assert isinstance(Bar.unset_attribute, Property)

    with pytest.raises(AttributeError):
        bar = Bar("dummy expr")
        bar.unset_attribute


def test_property_re_set_error():
    class Bar(AbstractSimpleExtractor):
        boo = Property[int]()

        def extract(self, element):
            return super().extract(element)

    bar = Bar("dummy expr")
    bar.boo = 0
    assert bar.boo == 0
    with pytest.raises(AttributeError):
        bar.boo = 1
    assert bar.boo == 0


def test_property_change_internal_value_success():
    class Bar(AbstractSimpleExtractor):
        boo = Property[int]()

        def extract(self, element):
            return super().extract(element)

    bar = Bar("dummy expr")
    bar.boo = 0
    assert bar.boo == 0
    Property.change_internal_value(bar, "boo", 1)
    assert bar.boo == 1


def test_property_change_internal_value_failure():
    class Bar(AbstractSimpleExtractor):
        boo = 1

        def extract(self, element):
            return super().extract(element)

    bar = Bar("dummy expr")
    with pytest.raises(AttributeError):
        Property.change_internal_value(bar, "boo", 1)
