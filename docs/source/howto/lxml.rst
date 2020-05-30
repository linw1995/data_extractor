========================
Extract HTML or XML Data
========================

The function to extract data from the html or xml file
powered by lxml_ to support XPath_, by cssselect_ to support CSS-Selectors_.

Run below command to install optional dependency.

.. code-block:: shell

    pip install "data_extractor[lxml]"  # For using XPath
    pip install "data_extractor[cssselect]"  # For using CSS-Selectors

Download RSS Sample file for demonstrate.

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

    assert (
        XPathExtractor("//channel/title/text()").extract_first(root)
        == "Liftoff News"
    )

Using :class:`data_extractor.lxml.TextCSSExtractor`
to extract all rss item links.

.. code-block:: python3

    from data_extractor import TextCSSExtractor

    assert TextCSSExtractor("item>link").extract(root) == [
        "http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp",
        "http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp",
        "http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp",
    ]

Using :class:`data_extractor.lxml.AttrCSSExtractor` to extract rss version.

.. code-block:: python3

    from data_extractor import AttrCSSExtractor

    assert AttrCSSExtractor("rss", attr="version").extract_first(root) == "2.0"

.. _lxml: https://lxml.de
.. _XPath: https://www.w3.org/TR/xpath-10/
.. _cssselect: https://cssselect.readthedocs.io/en/latest/
.. _CSS-Selectors: https://www.w3.org/TR/selectors-3/
