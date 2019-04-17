# Third Party Library
import pytest

# Dsipder Module
from data_extractor.html import XPathExtractor, fromstring
from data_extractor.item import Field, Item


@pytest.fixture(scope="module")
def text():
    return """
        <div class="author">
            <span class="author_name">Jack</span>
            <ul class="articles">
                <li class="article">
                    <h3 class="title">
                        Title 1
                    </h3>
                    <div class="content">
                        Content 1
                    </div>
                </li>
                <li class="article">
                    <h3 class="title">
                        Title 2
                    </h3>
                    <div class="content">
                        Content 2
                    </div>
                </li>
            </ul>
        </div>
    """


@pytest.fixture(scope="module")
def element(text):
    return fromstring(text)


def test_item_extract(element):
    class Article(Item):
        title = Field(XPathExtractor("normalize-space(./h3[@class='title'])"))
        content = Field(XPathExtractor("normalize-space(./div[@class='content'])"))

    class Author(Item):
        name = Field(XPathExtractor("./span[@class='author_name']/text()"))
        age = Field(XPathExtractor("./span[@class='age']/text()"), default=-1)
        articles = Article(XPathExtractor("./ul[@class='articles']/li"), is_many=True)
        favorites = Article(XPathExtractor("./ul[@class='favorites']/li"), is_many=True)
        pinned = Article(XPathExtractor("./div[@class='pinned']"), default=None)

    assert Author(XPathExtractor("//div[@class='author']")).extract(element) == {
        "name": "Jack",
        "age": -1,
        "articles": [
            {"title": "Title 1", "content": "Content 1"},
            {"title": "Title 2", "content": "Content 2"},
        ],
        "favorites": [],
        "pinned": None,
    }
