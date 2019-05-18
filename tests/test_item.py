# Standard Library
import inspect

from pathlib import Path

# Third Party Library
import pytest

# First Party Library
from data_extractor.exceptions import ExtractError
from data_extractor.item import Field, Item
from data_extractor.json import JSONExtractor
from data_extractor.lxml import CSSExtractor, TextCSSExtractor, XPathExtractor


@pytest.fixture
def element0():
    from lxml.html import fromstring

    text = """
        <ul class="articles">
            <li class="article">
                <div class="title">Title 1</div>
                <div class="content">Content 1</div>
            </li>
            <li class="article">
                <div class="title">Title 2</div>
            </li>
            <li class="article">
            </li>
        </ul>
    """
    return fromstring(text)


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (XPathExtractor, "//div[@class='title']/text()", "Title 1"),
        (XPathExtractor, "//div[@class='content']/text()", "Content 1"),
        (TextCSSExtractor, ".title", "Title 1"),
        (TextCSSExtractor, ".content", "Content 1"),
    ],
    ids=repr,
)
def test_field_extract(element0, Extractor, expr, expect):
    assert expect == Field(Extractor(expr)).extract(element0)


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (XPathExtractor, "//div[@class='title']/text()", ["Title 1", "Title 2"]),
        (XPathExtractor, "//div[@class='content']/text()", ["Content 1"]),
        (XPathExtractor, "//div[@class='notexists']/text()", []),
        (TextCSSExtractor, ".title", ["Title 1", "Title 2"]),
        (TextCSSExtractor, ".content", ["Content 1"]),
        (TextCSSExtractor, ".notexists", []),
    ],
    ids=repr,
)
def test_field_extract_with_is_many(element0, Extractor, expr, expect):
    assert expect == Field(Extractor(expr), is_many=True).extract(element0)


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (XPathExtractor, "//div[@class='notexists']/text()", "default"),
        (TextCSSExtractor, ".notexists", "default"),
    ],
    ids=repr,
)
def test_field_extract_with_default(element0, Extractor, expr, expect):
    assert expect == Field(Extractor(expr), default=expect).extract(element0)


@pytest.mark.parametrize(
    "Extractor,expr",
    [
        (XPathExtractor, "//div[@class='notexists']/text()"),
        (TextCSSExtractor, ".notexists"),
    ],
    ids=repr,
)
def test_field_extract_without_default(element0, Extractor, expr):
    extractor = Field(Extractor(expr))
    with pytest.raises(ExtractError) as catch:
        extractor.extract(element0)

    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element0


def test_field_parameters_conflict():
    with pytest.raises(ValueError):
        Field(TextCSSExtractor(".nomatter"), is_many=True, default=None)


def test_field_xpath_extract_result_not_list(element0):
    assert (
        Field(XPathExtractor("normalize-space(//div[@class='title'])")).extract(
            element0
        )
        == "Title 1"
    )


def test_field_xpath_extract_result_not_list_conflict_with_is_many(element0):
    with pytest.warns(UserWarning):
        Field(
            XPathExtractor("normalize-space(//div[@class='title'])"), is_many=True
        ).extract(element0)


@pytest.fixture
def element1():
    from lxml.html import fromstring

    text = """
        <ul class="articles">
            <li class="article">
                <div class="title">Title 1</div>
                <div class="content">Content 1</div>
            </li>
            <li class="article">
                <div class="title">Title 2</div>
                <div class="content">Content 2</div>
            </li>
        </ul>
    """
    return fromstring(text)


@pytest.fixture
def Article0():
    class Article(Item):
        title = Field(XPathExtractor("./div[@class='title']/text()"))
        content = Field(XPathExtractor("./div[@class='content']/text()"))

    return Article


def test_item_extract(element1, Article0):
    assert Article0(CSSExtractor("li.article"), is_many=True).extract(element1) == [
        {"title": "Title 1", "content": "Content 1"},
        {"title": "Title 2", "content": "Content 2"},
    ]


def test_item_extract_without_is_many(element1, Article0):
    assert Article0(CSSExtractor("li.article")).extract(element1) == {
        "title": "Title 1",
        "content": "Content 1",
    }


@pytest.fixture
def element2():
    from lxml.html import fromstring

    text = """
        <ul class="articles">
            <li class="article">
                <div class="title">Title 1</div>
                <div class="content">Content 1</div>
            </li>
            <li class="article">
                <div class="title">Title 2</div>
            </li>
        </ul>
    """
    return fromstring(text)


def test_item_extract_failure_when_last_field_missing(element2, Article0):
    extractor = Article0(CSSExtractor("li.article"), is_many=True)
    with pytest.raises(ExtractError) as catch:
        extractor.extract(element2)

    exc = catch.value
    assert len(exc.extractors) == 2
    assert exc.extractors[0] is Article0.content
    assert exc.extractors[1] is extractor
    assert exc.element is element2.xpath("//li[@class='article'][2]")[0]


def test_item_extract_success_without_is_many_when_last_field_missing(
    element2, Article0
):
    assert Article0(CSSExtractor("li.article")).extract(element2) == {
        "title": "Title 1",
        "content": "Content 1",
    }


def test_complex_item_extract_xml_data():
    from lxml.etree import fromstring

    sample_rss_path = Path(__file__).parent / "assets" / "sample-rss-2.xml"
    text = sample_rss_path.read_text()
    element = fromstring(text)

    class ChannelItem(Item):
        title = Field(XPathExtractor("./title/text()"), default="")
        link = Field(XPathExtractor("./link/text()"), default="")
        description = Field(XPathExtractor("./description/text()"))
        publish_date = Field(XPathExtractor("./pubDate/text()"))
        guid = Field(XPathExtractor("./guid/text()"))

    class Channel(Item):
        title = Field(XPathExtractor("./title/text()"))
        link = Field(XPathExtractor("./link/text()"))
        description = Field(XPathExtractor("./description/text()"))
        language = Field(XPathExtractor("./language/text()"))
        publish_date = Field(XPathExtractor("./pubDate/text()"))
        last_build_date = Field(XPathExtractor("./lastBuildDate/text()"))
        docs = Field(XPathExtractor("./docs/text()"))
        generator = Field(XPathExtractor("./generator/text()"))
        managing_editor = Field(XPathExtractor("./managingEditor/text()"))
        web_master = Field(XPathExtractor("./webMaster/text()"))

        items = ChannelItem(XPathExtractor("./item"), is_many=True)

    items_result = [
        {
            "title": "Star City",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp",
            "description": 'How do Americans get ready to work with Russians aboard the International Space Station? They take a crash course in culture, language and protocol at Russia\'s <a href="http://howe.iki.rssi.ru/GCTC/gctc_e.htm">Star City</a>.',
            "publish_date": "Tue, 03 Jun 2003 09:39:21 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/06/03.html#item573",
        },
        {
            "title": "",
            "link": "",
            "description": 'Sky watchers in Europe, Asia, and parts of Alaska and Canada will experience a <a href="http://science.nasa.gov/headlines/y2003/30may_solareclipse.htm">partial eclipse of the Sun</a> on Saturday, May 31st.',
            "publish_date": "Fri, 30 May 2003 11:06:42 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/30.html#item572",
        },
        {
            "title": "The Engine That Does More",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp",
            "description": "Before man travels to Mars, NASA hopes to design new engines that will let us fly through the Solar System more quickly.  The proposed VASIMR engine would do that.",
            "publish_date": "Tue, 27 May 2003 08:37:32 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/27.html#item571",
        },
        {
            "title": "Astronauts' Dirty Laundry",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp",
            "description": "Compared to earlier spacecraft, the International Space Station has many luxuries, but laundry facilities are not one of them.  Instead, astronauts have other options.",
            "publish_date": "Tue, 20 May 2003 08:56:02 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/20.html#item570",
        },
    ]
    assert ChannelItem(CSSExtractor("channel>item")).extract(element) == items_result[0]
    assert (
        ChannelItem(CSSExtractor("channel>item"), is_many=True).extract(element)
        == items_result
    )
    assert Channel(XPathExtractor("//channel")).extract(element) == {
        "title": "Liftoff News",
        "link": "http://liftoff.msfc.nasa.gov/",
        "description": "Liftoff to Space Exploration.",
        "language": "en-us",
        "publish_date": "Tue, 10 Jun 2003 04:00:00 GMT",
        "last_build_date": "Tue, 10 Jun 2003 09:41:01 GMT",
        "docs": "http://blogs.law.harvard.edu/tech/rss",
        "generator": "Weblog Editor 2.0",
        "managing_editor": "editor@example.com",
        "web_master": "webmaster@example.com",
        "items": items_result,
    }


def test_complex_item_extract_json_data(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")
        gender = Field(JSONExtractor("gender"), default=None)

    class UserResponse(Item):
        start = Field(JSONExtractor("start"), default=0)
        size = Field(JSONExtractor("size"))
        total = Field(JSONExtractor("total"))
        data = User(JSONExtractor("users[*]"), is_many=True)

    users_result = [
        {"uid": 0, "name": "Vang Stout", "gender": "female"},
        {"uid": 1, "name": "Jeannie Gaines", "gender": "male"},
        {"uid": 2, "name": "Guzman Hunter", "gender": "female"},
        {"uid": 3, "name": "Janine Gross", "gender": None},
        {"uid": 4, "name": "Clarke Patrick", "gender": "male"},
        {"uid": 5, "name": "Whitney Mcfadden", "gender": None},
    ]
    assert User(JSONExtractor("data.users[*]")).extract(data) == users_result[0]
    assert (
        User(JSONExtractor("data.users[*]"), is_many=True).extract(data) == users_result
    )
    assert UserResponse(JSONExtractor("data")).extract(data) == {
        "start": 0,
        "size": 5,
        "total": 100,
        "data": users_result,
    }


def test_misplacing():
    class ComplexExtractor(Item):
        pass

    with pytest.raises(ValueError):
        Field(extractor=ComplexExtractor(extractor=JSONExtractor("users[*]")))


def test_field_name_overwrite_item_parameter():
    with pytest.raises(SyntaxError) as catch:

        class User(Item):
            uid = Field(JSONExtractor("id"))
            name = Field(JSONExtractor("name"))

    exc = catch.value
    assert exc.filename == __file__
    assert exc.lineno == inspect.currentframe().f_lineno - 4
    assert exc.offset == 12
    assert exc.text == 'name = Field(JSONExtractor("name"))'


def test_avoid_field_name_overwriting_item_parameter(json0):
    data = json0

    with pytest.raises(SyntaxError):

        class User(Item):
            uid = Field(JSONExtractor("id"))
            name = Field(JSONExtractor("name"))

    class User(Item):  # noqa
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")

    assert User(JSONExtractor("data.users[*]")).extract(data) == {
        "uid": 0,
        "name": "Vang Stout",
    }


def test_special_field_name(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="user.name")

    assert User(JSONExtractor("data.users[*]")).extract(data) == {
        "uid": 0,
        "user.name": "Vang Stout",
    }


def test_special_field_name_in_the_nested_class_definition(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")

    class UserResponse(Item):
        _ = User(JSONExtractor("users[*]"), name="data")

    first_row = {"uid": 0, "name": "Vang Stout"}
    assert User(JSONExtractor("data.users[*]")).extract(data) == first_row
    assert UserResponse(JSONExtractor("data")).extract(data) == {"data": first_row}
