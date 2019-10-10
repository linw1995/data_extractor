Quickstarts
===========

Installation
------------

install the stable version

.. code-block:: shell

    pip install data-extractor

or install the latest version

.. code-block:: shell

    pip install git+https://github.com/linw1995/data_extractor.git@master

Usage
-----

Simple Extractor
++++++++++++++++

HTML or XML data
################

Powered by lxml_ to support XPath_, by cssselect_ to support `CSS Selectors`_.

.. _lxml: https://lxml.de
.. _XPath: https://www.w3.org/TR/xpath-10/
.. _cssselect: https://cssselect.readthedocs.io/en/latest/
.. _`CSS Selectors`: https://www.w3.org/TR/selectors-3/

Download RSS Sample file

.. code-block:: shell

    wget http://www.rssboard.org/files/sample-rss-2.xml

Parse it into :class:`data_extractor.lxml.Element`.

.. code-block:: python3

    from pathlib import Path

    from lxml.etree import fromstring

    root = fromstring(Path("sample-rss-2.xml").read_text())

Using :class:`data_extractor.lxml.XPathExtractor` to extract rss channel title.

.. code-block:: python3

    from data_extractor import XPathExtractor

    XPathExtractor("//channel/title/text()").extract_first(root)

Output:

.. code-block:: python3

    'Liftoff News'

Using :class:`data_extractor.lxml.TextCSSExtractor`
to extract all rss item links.

.. code-block:: python3

    from data_extractor import TextCSSExtractor

    TextCSSExtractor("item>link").extract(root)

Output:

.. code-block:: python3

    ['http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp',
     'http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp',
     'http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp']


Using :class:`data_extractor.lxml.AttrCSSExtractor` to extract rss version.

.. code-block:: python3

    from data_extractor import AttrCSSExtractor

    AttrCSSExtractor("rss", attr="version").extract_first(root)

Output:

.. code-block:: python3

    '2.0'

JSON Data
#########

Powered by python-jsonpath-rw_ and python-jsonpath-rw-ext_
to support JSONPath_.

.. _python-jsonpath-rw: https://github.com/kennknowles/python-jsonpath-rw
.. _python-jsonpath-rw-ext: https://python-jsonpath-rw-ext.readthedocs.org/en/latest/
.. _JSONPath: https://goessner.net/articles/JsonPath/

Example data

.. code-block:: json

    {"foo": [{"baz": 1}, {"baz": 2}]}

Using :class:`data_extractor.json.JSONExtractor` to extract data.

.. code-block:: python3

    from data_extractor import JSONExtractor

    JSONExtractor("foo[*].baz").extract(data)

Output:

.. code-block:: python3

    [1, 2]

Complex Extractor
+++++++++++++++++

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

    ChannelItem(XPathExtractor("//channel/item"), is_many=True).extract(root)

Output:

.. code-block:: json

    [
        {
            "title": "Star City",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp",
            "description": "How do Americans get ready to work with Russians aboard the International Space Station? They take a crash course in culture, language and protocol at Russia's <a href=\"http://howe.iki.rssi.ru/GCTC/gctc_e.htm\">Star City</a>.",
            "publish_date": "Tue, 03 Jun 2003 09:39:21 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/06/03.html#item573"
        },
        {
            "title": "",
            "link": "",
            "description": "Sky watchers in Europe, Asia, and parts of Alaska and Canada will experience a <a href=\"http://science.nasa.gov/headlines/y2003/30may_solareclipse.htm\">partial eclipse of the Sun</a> on Saturday, May 31st.",
            "publish_date": "Fri, 30 May 2003 11:06:42 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/30.html#item572"
        },
        {
            "title": "The Engine That Does More",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp",
            "description": "Before man travels to Mars, NASA hopes to design new engines that will let us fly through the Solar System more quickly.  The proposed VASIMR engine would do that.",
            "publish_date": "Tue, 27 May 2003 08:37:32 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/27.html#item571"
        },
        {
            "title": "Astronauts' Dirty Laundry",
            "link": "http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp",
            "description": "Compared to earlier spacecraft, the International Space Station has many luxuries, but laundry facilities are not one of them.  Instead, astronauts have other options.",
            "publish_date": "Tue, 20 May 2003 08:56:02 GMT",
            "guid": "http://liftoff.msfc.nasa.gov/2003/05/20.html#item570"
        }
    ]

Nested Complex Extractor
########################

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

        items = ChannelItem(XPathExtractor("./item"), is_many=True)

Extracting the rss channel data from file.

.. code-block:: python3

    from data_extractor import XPathExtractor

    Channel(XPathExtractor("//channel")).extract(root)

Output:

.. code-block:: json

    {
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
                "description": "How do Americans get ready to work with Russians aboard the International Space Station? They take a crash course in culture, language and protocol at Russia's <a href=\"http://howe.iki.rssi.ru/GCTC/gctc_e.htm\">Star City</a>.",
                "publish_date": "Tue, 03 Jun 2003 09:39:21 GMT",
                "guid": "http://liftoff.msfc.nasa.gov/2003/06/03.html#item573"
            },
            {
                "title": "",
                "link": "",
                "description": "Sky watchers in Europe, Asia, and parts of Alaska and Canada will experience a <a href=\"http://science.nasa.gov/headlines/y2003/30may_solareclipse.htm\">partial eclipse of the Sun</a> on Saturday, May 31st.",
                "publish_date": "Fri, 30 May 2003 11:06:42 GMT",
                "guid": "http://liftoff.msfc.nasa.gov/2003/05/30.html#item572"
            },
            {
                "title": "The Engine That Does More",
                "link": "http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp",
                "description": "Before man travels to Mars, NASA hopes to design new engines that will let us fly through the Solar System more quickly.  The proposed VASIMR engine would do that.",
                "publish_date": "Tue, 27 May 2003 08:37:32 GMT",
                "guid": "http://liftoff.msfc.nasa.gov/2003/05/27.html#item571"
            },
            {
                "title": "Astronauts' Dirty Laundry",
                "link": "http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp",
                "description": "Compared to earlier spacecraft, the International Space Station has many luxuries, but laundry facilities are not one of them.  Instead, astronauts have other options.",
                "publish_date": "Tue, 20 May 2003 08:56:02 GMT",
                "guid": "http://liftoff.msfc.nasa.gov/2003/05/20.html#item570"
            }
        ]
    }


Simplifying Complex Extractor
#############################

A complex extractor can be simplified
into a simple extractor
by using :meth:`data_extractor.item.Item.simplify`.
And extracting first channel item from file.

.. code-block:: python3

    from data_extractor import XPathExtractor

    simple_extractor = ChannelItem(XPathExtractor("//channel/item"), is_many=True).simplify()
    simple_extractor.extract_first(root)

Output:

.. code-block:: json

    {
        "title": "Star City",
        "link": "http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp",
        "description": "How do Americans get ready to work with Russians aboard the International Space Station? They take a crash course in culture, language and protocol at Russia's <a href=\"http://howe.iki.rssi.ru/GCTC/gctc_e.htm\">Star City</a>.",
        "publish_date": "Tue, 03 Jun 2003 09:39:21 GMT",
        "guid": "http://liftoff.msfc.nasa.gov/2003/06/03.html#item573"
    }
