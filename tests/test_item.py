# Standard Library
import inspect
import linecache
import reprlib

from pathlib import Path
from types import FunctionType

# Third Party Library
import pytest

# First Party Library
from data_extractor.exceptions import ExtractError
from data_extractor.item import Field, Item
from data_extractor.json import JSONExtractor
from data_extractor.lxml import CSSExtractor, TextCSSExtractor, XPathExtractor
from data_extractor.utils import is_complex_extractor, is_simple_extractor


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


@pytest.fixture(
    params=["extractor", "name", "default", "is_many", "_field_names", "built"]
)
def item_property(request):
    return request.param


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
def test_field_extract(element0, Extractor, expr, expect, build_first):
    field = Field(Extractor(expr))
    assert not field.built
    assert not field.extractor.built
    if build_first:
        field.build()
        assert field.built
        assert field.extractor.built

    assert expect == field.extract(element0)
    assert field.built
    assert field.extractor.built


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (
            XPathExtractor,
            "//div[@class='title']/text()",
            ["Title 1", "Title 2"],
        ),
        (XPathExtractor, "//div[@class='content']/text()", ["Content 1"]),
        (XPathExtractor, "//div[@class='notexists']/text()", []),
        (TextCSSExtractor, ".title", ["Title 1", "Title 2"]),
        (TextCSSExtractor, ".content", ["Content 1"]),
        (TextCSSExtractor, ".notexists", []),
    ],
    ids=repr,
)
def test_field_extract_with_is_many(
    element0, Extractor, expr, expect, build_first
):
    field = Field(Extractor(expr), is_many=True)
    assert not field.built
    assert not field.extractor.built
    if build_first:
        field.build()
        assert field.built
        assert field.extractor.built

    assert expect == field.extract(element0)
    assert field.built
    assert field.extractor.built


@pytest.mark.parametrize(
    "Extractor,expr,expect",
    [
        (XPathExtractor, "//div[@class='notexists']/text()", "default"),
        (TextCSSExtractor, ".notexists", "default"),
    ],
    ids=repr,
)
def test_field_extract_with_default(
    element0, Extractor, expr, expect, build_first
):
    field = Field(Extractor(expr), default=expect)
    assert not field.built
    assert not field.extractor.built
    if build_first:
        field.build()
        assert field.built
        assert field.extractor.built

    assert expect == field.extract(element0)
    assert field.built
    assert field.extractor.built


@pytest.mark.parametrize(
    "Extractor,expr",
    [
        (XPathExtractor, "//div[@class='notexists']/text()"),
        (TextCSSExtractor, ".notexists"),
    ],
    ids=repr,
)
def test_field_extract_without_default(element0, Extractor, expr, build_first):
    extractor = Field(Extractor(expr))
    assert not extractor.built
    assert not extractor.extractor.built
    if build_first:
        extractor.build()
        assert extractor.built
        assert extractor.extractor.built

    with pytest.raises(ExtractError) as catch:
        extractor.extract(element0)

    assert extractor.built
    assert extractor.extractor.built

    exc = catch.value
    assert len(exc.extractors) == 1
    assert exc.extractors[0] is extractor
    assert exc.element is element0


def test_field_parameters_conflict():
    with pytest.raises(ValueError):
        Field(TextCSSExtractor(".nomatter"), is_many=True, default=None)


def test_field_xpath_extract_result_not_list(element0, build_first):
    field = Field(XPathExtractor("normalize-space(//div[@class='title'])"))
    assert not field.built
    assert not field.extractor.built
    if build_first:
        field.build()
        assert field.built
        assert field.extractor.built

    assert field.extract(element0) == "Title 1"
    assert field.built
    assert field.extractor.built


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


def test_item_extract(element1, Article0, build_first):
    item = Article0(CSSExtractor("li.article"), is_many=True)
    assert not item.built
    assert not item.extractor.built
    assert not item.title.built
    assert not item.content.built
    if build_first:
        item.build()
        assert item.built
        assert item.extractor.built
        assert item.title.built
        assert item.content.built

    assert item.extract(element1) == [
        {"title": "Title 1", "content": "Content 1"},
        {"title": "Title 2", "content": "Content 2"},
    ]
    assert item.built
    assert item.extractor.built
    assert item.title.built
    assert item.content.built


def test_item_extract_without_is_many(element1, Article0, build_first):
    item = Article0(CSSExtractor("li.article"))
    assert not item.built
    assert not item.extractor.built
    assert not item.title.built
    assert not item.content.built
    if build_first:
        item.build()
        assert item.built
        assert item.extractor.built
        assert item.title.built
        assert item.content.built

    assert item.extract(element1) == {
        "title": "Title 1",
        "content": "Content 1",
    }
    assert item.built
    assert item.extractor.built
    assert item.title.built
    assert item.content.built


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


def test_item_extract_failure_when_last_field_missing(
    element2, Article0, build_first
):
    item = Article0(CSSExtractor("li.article"), is_many=True)
    assert not item.built
    assert not item.extractor.built
    assert not item.title.built
    assert not item.content.built
    if build_first:
        item.build()
        assert item.built
        assert item.extractor.built
        assert item.title.built
        assert item.content.built

    with pytest.raises(ExtractError) as catch:
        item.extract(element2)

    assert item.built
    assert item.extractor.built
    assert item.title.built
    assert item.content.built

    exc = catch.value
    assert len(exc.extractors) == 2
    assert exc.extractors[0] is Article0.content
    assert exc.extractors[1] is item
    assert exc.element is element2.xpath("//li[@class='article'][2]")[0]


def test_item_extract_success_without_is_many_when_last_field_missing(
    element2, Article0, build_first
):
    item = Article0(CSSExtractor("li.article"))
    assert not item.built
    assert not item.extractor.built
    assert not item.title.built
    assert not item.content.built
    if build_first:
        item.build()
        assert item.built
        assert item.extractor.built
        assert item.title.built
        assert item.content.built

    assert item.extract(element2) == {
        "title": "Title 1",
        "content": "Content 1",
    }
    assert item.built
    assert item.extractor.built
    assert item.title.built
    assert item.content.built


def test_complex_item_extract_xml_data(build_first):
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
            "description": (
                "How do Americans get ready to work "
                "with Russians aboard the International Space Station? "
                "They take a crash course in culture, "
                "language and protocol at Russia's "
                '<a href="http://howe.iki.rssi.ru/GCTC/gctc_e.htm">Star City</a>.'
            ),
            "publish_date": "Tue, 03 Jun 2003 09:39:21 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/06/03.html#item573",
        },
        {
            "title": "",
            "link": "",
            "description": (
                "Sky watchers in Europe, Asia, and parts of Alaska and Canada "
                "will experience a "
                '<a href="http://science.nasa.gov/headlines/y2003/30may_solareclipse.htm">'  # noqa: B950
                "partial eclipse of the Sun"
                "</a> on Saturday, May 31st."
            ),
            "publish_date": "Fri, 30 May 2003 11:06:42 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/30.html#item572",
        },
        {
            "title": "The Engine That Does More",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp",
            "description": (
                "Before man travels to Mars, "
                "NASA hopes to design new engines "
                "that will let us fly through the Solar System more quickly.  "
                "The proposed VASIMR engine would do that."
            ),
            "publish_date": "Tue, 27 May 2003 08:37:32 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/27.html#item571",
        },
        {
            "title": "Astronauts' Dirty Laundry",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp",
            "description": (
                "Compared to earlier spacecraft, "
                "the International Space Station has many luxuries, "
                "but laundry facilities are not one of them.  "
                "Instead, astronauts have other options."
            ),
            "publish_date": "Tue, 20 May 2003 08:56:02 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/20.html#item570",
        },
    ]
    item = ChannelItem(CSSExtractor("channel>item"))
    if build_first:
        item.build()
    assert item.extract(element) == items_result[0]

    item = ChannelItem(CSSExtractor("channel>item"), is_many=True)
    if build_first:
        item.build()
    assert item.extract(element) == items_result

    item = Channel(XPathExtractor("//channel"))
    if build_first:
        item.build()
    assert item.extract(element) == {
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


def test_complex_item_extract_json_data(json0, build_first):
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
    item = User(JSONExtractor("data.users[*]"))
    if build_first:
        item.build()
    assert item.extract(data) == users_result[0]

    item = User(JSONExtractor("data.users[*]"), is_many=True)
    if build_first:
        item.build()
    assert item.extract(data) == users_result

    item = UserResponse(JSONExtractor("data"))
    if build_first:
        item.build()
    assert item.extract(data) == {
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


def test_field_overwrites_item_property_common(stack_frame_support):
    with pytest.raises(SyntaxError) as catch:

        class User(Item):
            uid = Field(JSONExtractor("id"))
            name = Field(JSONExtractor("name"))

    exc = catch.value
    if stack_frame_support:
        assert exc.filename == __file__
        assert exc.lineno == inspect.currentframe().f_lineno - 5
        assert exc.offset == 12
        assert exc.text == 'name = Field(JSONExtractor("name"))'
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert exc.text == "name=Field(JSONExtractor('name'))"


def test_field_overwrites_item_property_oneline(stack_frame_support):
    with pytest.raises(SyntaxError) as catch:
        # fmt: off
        class Parameter(Item): name = Field(XPathExtractor("./span[@class='name']"))  # noqa: B950, E701
        # fmt: on

    exc = catch.value
    if stack_frame_support:
        assert exc.filename == __file__
        assert exc.lineno == inspect.currentframe().f_lineno - 6
        assert exc.offset == 8
        assert (
            exc.text
            == "class Parameter(Item): name = Field(XPathExtractor(\"./span[@class='name']\"))  # noqa: B950, E701"
        )
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert (
            exc.text
            == """name=Field(XPathExtractor("./span[@class='name']"))"""
        )


def test_field_overwrites_item_parameter_type_creation(
    stack_frame_support, item_property
):
    with pytest.raises(SyntaxError) as catch:
        # fmt: off
        type("Parameter", (Item,), {item_property: Field(XPathExtractor("./span[@class='name']"))})  # noqa: E950
        # fmt: on

    exc = catch.value
    if stack_frame_support:
        assert exc.filename == __file__
        assert exc.lineno == inspect.currentframe().f_lineno - 6
        assert exc.offset == 8
        assert (
            exc.text
            == """
        type("Parameter", (Item,), {item_property: Field(XPathExtractor("./span[@class='name']"))})  # noqa: E950
        """.strip()
        )
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert (
            exc.text
            == f"""{item_property}=Field(XPathExtractor("./span[@class='name']"))"""
        )


@pytest.mark.parametrize(
    "template, text_template",
    [
        (
            """
    type("Parameter",(Item,),{%r: Field(XPathExtractor("./span[@class='name']"))})
    """.strip(),
            """%s=Field(XPathExtractor("./span[@class='name']"))""",
        ),
        (
            "class Parameter(Item): %s = Field(XPathExtractor(\"./span[@class='name']\"))  # noqa: B950, E701",
            """%s=Field(XPathExtractor(\"./span[@class='name']\"))""",
        ),
        (
            """
class User(Item):
    uid = Field(JSONExtractor("id")); %s = Field(JSONExtractor("name"))
    """.strip(),
            "%s=Field(JSONExtractor('name'))",
        ),
        (
            """
class User(Item):
    uid = Field(JSONExtractor("id"))
    %s = Field(JSONExtractor("name"))
    """.strip(),
            "%s=Field(JSONExtractor('name'))",
        ),
    ],
    ids=reprlib.repr,
)
def test_field_overwrites_item_property_in_repl(
    template, text_template, item_property, stack_frame_support
):
    with pytest.raises(SyntaxError) as catch:
        exec(template % (item_property,))

    exc = catch.value
    assert exc.filename is None
    assert exc.lineno is None
    assert exc.offset is None
    assert exc.text == text_template % (item_property,)


@pytest.mark.parametrize(
    "template",
    [
        """type("Parameter",(Item,),{%r: Field(XPathExtractor("./span[@class='name']"))})""",  # noqa: B950
        "class Parameter(Item): %s = Field(XPathExtractor(\"./span[@class='name']\"))",  # noqa: B950
    ],
    ids=reprlib.repr,
)
def test_field_overwrites_item_property_oneline_in_script(
    tmp_path, stack_frame_support, template, item_property
):
    source_code = template % (item_property,)
    tmp_file = tmp_path / "foo.py"
    tmp_file.write_text(source_code)
    tmp_file = str(tmp_file)
    linecache.updatecache(tmp_file)

    with pytest.raises(SyntaxError) as catch:
        exec(compile(source_code, tmp_file, "exec"))

    exc = catch.value
    if stack_frame_support:
        assert exc.filename == tmp_file
        assert exc.lineno == 1
        assert exc.offset == 0
        assert exc.text == source_code
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert (
            exc.text
            == f"""{item_property}=Field(XPathExtractor("./span[@class='name']"))"""
        )


def test_field_overwrites_item_property_common_in_script(
    tmp_path, stack_frame_support, item_property
):
    source_code = f"""
class User(Item):
    uid = Field(JSONExtractor("id"))
    {item_property} = Field(JSONExtractor({item_property!r}))
    """.strip()

    tmp_file = tmp_path / "foo.py"
    tmp_file.write_text(source_code)
    tmp_file = str(tmp_file)
    linecache.updatecache(tmp_file)

    with pytest.raises(SyntaxError) as catch:
        exec(compile(source_code, tmp_file, "exec"))

    exc = catch.value
    if stack_frame_support:
        assert exc.filename == tmp_file
        assert exc.lineno == 3
        assert exc.offset == 4
        assert (
            exc.text
            == f"{item_property} = Field(JSONExtractor({item_property!r}))"
        )
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert (
            exc.text
            == f"{item_property}=Field(JSONExtractor({item_property!r}))"
        )


def test_avoid_field_overwriting_item_parameter(
    json0, stack_frame_support, build_first
):
    data = json0

    with pytest.raises(SyntaxError):

        class User(Item):
            uid = Field(JSONExtractor("id"))
            name = Field(JSONExtractor("name"))

    class User(Item):  # noqa: F811
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")

    item = User(JSONExtractor("data.users[*]"))
    if build_first:
        item.build()
    assert item.extract(data) == {"uid": 0, "name": "Vang Stout"}


def test_special_field_name(json0, build_first):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="user.name")

    item = User(JSONExtractor("data.users[*]"))
    if build_first:
        item.build()
    assert item.extract(data) == {"uid": 0, "user.name": "Vang Stout"}


def test_special_field_in_the_nested_class_definition(json0, build_first):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")

    class UserResponse(Item):
        _ = User(JSONExtractor("users[*]"), name="data")

    first_row = {"uid": 0, "name": "Vang Stout"}
    item = User(JSONExtractor("data.users[*]"))
    if build_first:
        item.build()
    assert item.extract(data) == first_row

    item = UserResponse(JSONExtractor("data"))
    if build_first:
        item.build()
    assert item.extract(data) == {"data": first_row}


@pytest.fixture
def json1():
    return {
        "id": 1,
        "username": "Jack",
        "count_follower": 100,
        "count_following": 1,
        "count_like": 1_000_000,
    }


def test_item_extractor_is_none(json1, build_first):
    data = json1

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("username"))

    item = User()
    if build_first:
        item.build()

    assert item.extract(data) == {"uid": 1, "username": "Jack"}

    item.is_many = True
    assert item.extract([data]) == [{"uid": 1, "username": "Jack"}]


def test_nested_item_extractor_is_none(json1, build_first):
    data = json1

    class Count(Item):
        follower = Field(JSONExtractor("count_follower"))
        following = Field(JSONExtractor("count_following"))
        like = Field(JSONExtractor("count_like"))

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("username"))
        count = Count()

    item = User()
    if build_first:
        item.build()

    assert item.extract(data) == {
        "uid": 1,
        "username": "Jack",
        "count": {"follower": 100, "following": 1, "like": 1_000_000},
    }

    item.is_many = True
    assert item.extract([data]) == [
        {
            "uid": 1,
            "username": "Jack",
            "count": {"follower": 100, "following": 1, "like": 1_000_000},
        }
    ]


@pytest.fixture(params=[True, False], ids=lambda x: f"before_simplify={x!r}")
def simplify_first(request):
    return request.param


def test_simplify(json0, build_first, simplify_first):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")
        gender = Field(JSONExtractor("gender"), default=None)

    item = User(JSONExtractor("data.users[*]"))
    if not simplify_first and build_first:
        item.build()
    extractor = item.simplify()
    if simplify_first and build_first:
        extractor.build()
    users_result = [
        {"uid": 0, "name": "Vang Stout", "gender": "female"},
        {"uid": 1, "name": "Jeannie Gaines", "gender": "male"},
        {"uid": 2, "name": "Guzman Hunter", "gender": "female"},
        {"uid": 3, "name": "Janine Gross", "gender": None},
        {"uid": 4, "name": "Clarke Patrick", "gender": "male"},
        {"uid": 5, "name": "Whitney Mcfadden", "gender": None},
    ]
    assert isinstance(extractor, JSONExtractor)
    assert is_simple_extractor(extractor)
    assert not is_complex_extractor(extractor)
    assert repr(extractor) == "UserSimplified('data.users[*]')"
    assert extractor.expr == "data.users[*]"
    assert extractor.extract_first(data) == users_result[0]
    assert extractor.extract(data) == users_result


def test_modify_simplified_item(json0, build_first, simplify_first):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")
        gender = Field(JSONExtractor("gender"), default=None)

    complex_extractor = User(JSONExtractor("data.users[*]"))
    if not simplify_first and build_first:
        complex_extractor.build()
    extractor = complex_extractor.simplify()
    if simplify_first and build_first:
        extractor.build()
    assert complex_extractor.extractor.expr == extractor.expr
    extractor.expr = "data.users[0]"
    assert complex_extractor.extractor.expr != extractor.expr

    assert isinstance(extractor, JSONExtractor)
    assert is_simple_extractor(extractor)
    assert not is_complex_extractor(extractor)
    assert repr(extractor) == "UserSimplified('data.users[0]')"

    assert extractor.extract_first(data) == {
        "uid": 0,
        "name": "Vang Stout",
        "gender": "female",
    }
    assert extractor.extract(data) == [
        {"uid": 0, "name": "Vang Stout", "gender": "female"}
    ]


def test_simplified_item_extractor_is_none(json0, build_first, simplify_first):
    data = json0["data"]["users"][0]

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")
        gender = Field(JSONExtractor("gender"), default=None)

    complex_extractor = User()
    if not simplify_first and build_first:
        complex_extractor.build()
    extractor = complex_extractor.simplify()
    if simplify_first and build_first:
        extractor.build()
    assert not isinstance(extractor, JSONExtractor)
    assert is_simple_extractor(extractor)
    assert not is_complex_extractor(extractor)
    assert repr(extractor) == "UserSimplified(None)"
    assert extractor.extract_first([data]) == {
        "uid": 0,
        "name": "Vang Stout",
        "gender": "female",
    }

    assert extractor.extract([data]) == [
        {"uid": 0, "name": "Vang Stout", "gender": "female"}
    ]


def test_inheritance(json0):
    data = json0["data"]["users"][0]

    class User(Item):
        uid = Field(JSONExtractor("id"))

    class UserWithGender(User):
        gender = Field(JSONExtractor("gender"))

    assert User().extract(data) == {"uid": 0}
    assert UserWithGender().extract(data) == {"uid": 0, "gender": "female"}


def test_field_overwrites_bases_method_in_item(stack_frame_support):
    with pytest.raises(SyntaxError) as catch:

        class User(Item):
            field_names = Field(JSONExtractor("field_names"))

    exc = catch.value
    if stack_frame_support:
        assert exc.filename == __file__
        assert exc.lineno == inspect.currentframe().f_lineno - 5
        assert exc.offset == 12
        assert exc.text == 'field_names = Field(JSONExtractor("field_names"))'
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert exc.text == "field_names=Field(JSONExtractor('field_names'))"


def test_field_overwrites_method_in_item(stack_frame_support):
    exc = None
    try:

        class User(Item):
            baz = Field(JSONExtractor("baz"))

            def baz(self):
                pass

    except Exception as exc_:
        exc = exc_

    if stack_frame_support:
        assert isinstance(exc, SyntaxError)
        assert exc.filename == __file__
        assert exc.lineno == inspect.currentframe().f_lineno - 9
        assert exc.offset == 12
        assert exc.text == "def baz(self):"
    else:
        assert exc is None


def test_method_overwrites_field_in_item(stack_frame_support):
    exc = None
    try:

        class User(Item):
            def baz(self):
                pass

            baz = Field(JSONExtractor("baz"))  # noqa: F811

    except Exception as exc_:
        exc = exc_

    if stack_frame_support:
        assert isinstance(exc, SyntaxError)
        assert exc.filename == __file__
        assert exc.lineno == inspect.currentframe().f_lineno - 8
        assert exc.offset == 12
        assert exc.text == 'baz = Field(JSONExtractor("baz"))  # noqa: F811'
    else:
        assert exc is None


@pytest.mark.xfail(reason="can't get the source code from python repl")
@pytest.mark.parametrize(
    "source_code",
    [
        """
class User(Item):
    baz = Field(JSONExtractor("baz"))

    def baz(self):
        pass
    """,
        """
class User(Item):
    def baz(self):
        pass

    baz = Field(JSONExtractor("baz"))
    """,
    ],
    ids=reprlib.repr,
)
def test_field_overwrites_method_in_item_in_repl(
    source_code, stack_frame_support
):
    with pytest.raises(SyntaxError):
        exec(source_code)


@pytest.mark.parametrize(
    "source_code, text",
    [
        (
            """
class User(Item):
    field_names = Field(JSONExtractor("field_names"))
    """,
            "field_names=Field(JSONExtractor('field_names'))",
        ),
        (
            """
class User(Item):
    extract = Field(JSONExtractor("extract"))
    """,
            "extract=Field(JSONExtractor('extract'))",
        ),
        (
            """
class User(Item):
    simplify = Field(JSONExtractor("simplify"))
    """,
            "simplify=Field(JSONExtractor('simplify'))",
        ),
    ],
    ids=reprlib.repr,
)
def test_field_overwrites_bases_method_in_item_in_repl(
    source_code, text, stack_frame_support
):
    with pytest.raises(SyntaxError) as catch:
        exec(source_code)
    exc = catch.value
    assert exc.filename is None
    assert exc.lineno is None
    assert exc.offset is None
    assert exc.text == text


@pytest.mark.parametrize(
    "source_code, lineno, offset, text",
    [
        (
            """
class User(Item):
    field_names = Field(JSONExtractor("field_names"))
    """,
            3,
            4,
            'field_names = Field(JSONExtractor("field_names"))',
        ),
        (
            """
class User(Item):
    extract = Field(JSONExtractor("extract"))
    """,
            3,
            4,
            'extract = Field(JSONExtractor("extract"))',
        ),
        (
            """
class User(Item):
    simplify = Field(JSONExtractor("simplify"))
    """,
            3,
            4,
            'simplify = Field(JSONExtractor("simplify"))',
        ),
    ],
    ids=reprlib.repr,
)
def test_field_overwrites_bases_method_in_item_in_script(
    tmp_path, source_code, lineno, offset, text, stack_frame_support
):
    tmp_file = tmp_path / "foo.py"
    tmp_file.write_text(source_code)
    tmp_file = str(tmp_file)
    linecache.updatecache(tmp_file)

    exc = None
    try:
        exec(compile(source_code, tmp_file, "exec"))
    except Exception as exc_:
        exc = exc_

    assert isinstance(exc, SyntaxError)
    if stack_frame_support:
        assert exc.filename == tmp_file
        assert exc.lineno == lineno
        assert exc.offset == offset
        assert exc.text == text
    else:
        assert exc.filename is None
        assert exc.lineno is None
        assert exc.offset is None
        assert exc.text == text.replace(" ", "").replace('"', "'")


@pytest.mark.parametrize(
    "source_code, lineno, offset, text",
    [
        (
            """
class User(Item):
    baz = Field(JSONExtractor("baz"))

    def baz(self):
        pass
    """,
            5,
            4,
            "def baz(self):",
        ),
        (
            """
class User(Item):
    def baz(self):
        pass

    baz = Field(JSONExtractor("baz"))
            """,
            6,
            4,
            'baz = Field(JSONExtractor("baz"))',
        ),
        (
            """
class User(Item):
    def baz(self):
        pass

    boo = [None]
    baz = boo[0] = Field(JSONExtractor("baz"))
    """,
            7,
            4,
            'baz = boo[0] = Field(JSONExtractor("baz"))',
        ),
    ],
    ids=reprlib.repr,
)
def test_field_overwrites_method_in_item_in_script(
    tmp_path, source_code, lineno, offset, text, stack_frame_support
):
    tmp_file = tmp_path / "foo.py"
    tmp_file.write_text(source_code)
    tmp_file = str(tmp_file)
    linecache.updatecache(tmp_file)

    exc = None
    try:
        exec(compile(source_code, tmp_file, "exec"))
    except Exception as exc_:
        exc = exc_

    if stack_frame_support:
        assert isinstance(exc, SyntaxError)
        assert exc.filename == tmp_file
        assert exc.lineno == lineno
        assert exc.offset == offset
        assert exc.text == text
    else:
        assert exc is None


def test_avoid_method_overwriting_field(stack_frame_support):
    data = {"baz": "baz", "boo": "boo"}

    exc = None
    try:

        class User(Item):
            baz = Field(JSONExtractor("baz"))

            def baz(self):
                pass

    except Exception as exc_:
        exc = exc_

    if stack_frame_support:
        assert isinstance(exc, SyntaxError)
    else:
        assert exc is None
        assert User().extract(data) == {}
        assert isinstance(User.baz, FunctionType)

    class User(Item):  # noqa: F811
        baz_ = Field(JSONExtractor("baz"), name="baz")

        def baz(self):
            pass

    assert User().extract(data) == {"baz": "baz"}


def test_avoid_field_overwriting_method(stack_frame_support):

    data = {"baz": "baz", "boo": "boo"}

    exc = None
    try:

        class User(Item):
            def baz(self):
                pass

            baz = Field(JSONExtractor("baz"))  # noqa: F811

    except Exception as exc_:
        exc = exc_

    if stack_frame_support:
        assert isinstance(exc, SyntaxError)
    else:
        assert exc is None
        assert User().extract(data) == {"baz": "baz"}
        assert isinstance(User.baz, Field)

    class User(Item):  # noqa: F811
        baz_ = Field(JSONExtractor("baz"), name="baz")

        def baz(self):
            pass

    assert User().extract(data) == {"baz": "baz"}


def test_avoid_field_overwriting_bases_method(stack_frame_support):
    data = {"field_names": ["field_names"], "baz": "baz"}

    with pytest.raises(SyntaxError):

        class User(Item):
            field_names = Field(JSONExtractor("field_names"))

    class User(Item):  # noqa: F811
        field_names_ = Field(JSONExtractor("field_names"), name="field_names")

    assert User().extract(data) == {"field_names": ["field_names"]}


def test_item_build_implicitly(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))

    item = User(JSONExtractor("data.users[0]"))
    assert not item.built
    assert not item.extractor.built
    assert not item.uid.built

    assert item.extract(data) == {"uid": 0}

    assert item.built
    assert item.extractor.built
    assert item.uid.built


def test_item_rebuild(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))

    item = User(JSONExtractor("data.users[0]"))
    assert not item.built
    assert not item.extractor.built
    assert not item.uid.built

    assert item.extract(data) == {"uid": 0}
    assert item.built
    assert item.extractor.built
    assert item.uid.built

    item.extractor = JSONExtractor("data.users[1]")
    assert not item.built
    assert not item.extractor.built
    assert item.uid.built

    assert item.extract(data) == {"uid": 1}
    assert item.built
    assert item.extractor.built
    assert item.uid.built


def test_item_build_explicitly(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))

    item = User(JSONExtractor("data.users[0]"))
    assert not item.built
    assert not item.extractor.built
    assert not item.uid.built

    item.build()
    assert item.built
    assert item.extractor.built
    assert item.uid.built
    assert item.extract(data) == {"uid": 0}


def test_modify_built_item(json0):
    data = json0["data"]["users"][0]

    class User(Item):
        uid = Field(JSONExtractor("id"))

    item = User(JSONExtractor("user"))
    assert not item.built
    assert not item.extractor.built
    assert not item.uid.built

    item.build()
    assert item.built
    assert item.extractor.built
    assert item.uid.built

    item.extractor = None
    assert not item.built
    assert item.uid.built

    assert item.extract(data) == {"uid": 0}
    assert item.built
