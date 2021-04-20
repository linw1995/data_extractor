# Standard Library
from collections import namedtuple

# Third Party Library
import pytest

# First Party Library
from data_extractor.item import RV, Field, Item
from data_extractor.json import JSONExtractor

# Local Folder
from .utils import D


def test_field_with_type():
    StrField = Field[str]
    f = StrField(D())
    assert f.type is str
    assert f.extract(1) == "1"

    f = Field[str](D())
    assert f.type is str
    assert f.extract(1) == "1"

    assert Field[str](D()).extract(1) == "1"


def test_field_with_convertor():
    f = Field(D(), convertor=lambda x: str(x).upper())
    assert f.type is None
    assert f.extract("abc") == "ABC"
    f = Field(D(), type=str, convertor=lambda x: str(x).upper())
    assert f.type is str
    assert f.extract("abc") == "ABC"


@pytest.mark.usefixtures("json_extractor_backend")
def test_item_with_type():
    class Article(Item[RV]):
        title = Field[str](JSONExtractor("title"))

    ArticleTuple = namedtuple("ArticleTuple", "title")
    article = Article[ArticleTuple]()
    rv = article.extract({"title": "example"})
    assert isinstance(rv, ArticleTuple)
    assert rv.title == "example"
