==================
Complex Extracting
==================

.. include:: lxml.rst
    :start-line: 7
    :end-before: Using

Defining :class:`ChannelItem` class, then extracting the data.

.. code-block:: python3

    from data_extractor import Field, Item, XPathExtractor


    class ChannelItem(Item):
        title = Field(XPathExtractor("./title/text()"), default="")
        link = Field(XPathExtractor("./link/text()"), default="")
        description = Field(XPathExtractor("./description/text()"))
        publish_date = Field(XPathExtractor("./pubDate/text()"))
        guid = Field(XPathExtractor("./guid/text()"))

Extracting all channel items from file.

.. code-block:: python3

    from data_extractor import XPathExtractor

    extractor = ChannelItem(XPathExtractor("//channel/item"), is_many=True)
    assert extractor.extract(root)[:2] == [
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
    ]

Nested Extractors
~~~~~~~~~~~~~~~~~

Defining :class:`Channel` class with :class:`ChannelItem`.

.. code-block:: python3

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

        items = ChannelItem(XPathExtractor("./item[position()<3]"), is_many=True)

Extracting the rss channel data from file.

.. code-block:: python3

    from data_extractor import XPathExtractor

    extractor = Channel(XPathExtractor("//channel"))
    assert extractor.extract(root) == {
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
        "items": [
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
        ],
    }

Simplifying Complex Extractor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A complex extractor can be simplified
into a simple extractor
by using :meth:`data_extractor.item.Item.simplify`.

.. code-block:: python3

    from data_extractor import XPathExtractor

    complex_extractorra = ChannelItem(XPathExtractor("//channel/item"))
    simple_extractor = complex_extractor.simplify()

    complex_extractor.is_many = False
    assert simple_extractor.extract_first(root) == complex_extractor.extract(root)

    complex_extractor.is_many = True
    assert simple_extractor.extract(root) == complex_extractor.extract(root)

Set Paramater Extractor Be None To Extract Data From Root
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python3

    from data_extractor import Item, Field, JSONExtractor


    class User(Item):
        nickname = Field(JSONExtractor("name"))
        age = Field(JSONExtractor("age"))
        raw = Field()


    assert User().extract({"name": "john", "age": 17, "gender": "male"}) == {
        "nickname": "john",
        "age": 17,
        "raw": {"name": "john", "age": 17, "gender": "male"},
    }

Avoid Field Overwrites Property Or Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid complex extractor's field overwrites its property or method,
use the parameter **name** of the complex extractor.

.. code-block:: python3

    from data_extractor import Field, Item, JSONExtractor


    class User(Item):
        name_ = Field(JSONExtractor("name"), name="name")


    assert User().extract({"name": "john", "age": 17}) == {"name": "john"}
