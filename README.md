[![license](https://img.shields.io/github/license/linw1995/data_extractor.svg)](https://github.com/linw1995/data_extractor/blob/master/LICENSE)
[![Pypi Status](https://img.shields.io/pypi/status/data_extractor.svg)](https://pypi.org/project/data_extractor)
[![Python version](https://img.shields.io/pypi/pyversions/data_extractor.svg)](https://pypi.org/project/data_extractor)
[![Package version](https://img.shields.io/pypi/v/data_extractor.svg)](https://pypi.org/project/data_extractor)
[![GitHub last commit](https://img.shields.io/github/last-commit/linw1995/data_extractor.svg)](https://github.com/linw1995/data_extractor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://travis-ci.org/linw1995/data_extractor.svg?branch=master)](https://travis-ci.org/linw1995/data_extractor)
[![codecov](https://codecov.io/gh/linw1995/data_extractor/branch/master/graph/badge.svg)](https://codecov.io/gh/linw1995/data_extractor)

# Data Extractor

Combine **XPath**, **CSS Selector** and **JSONPath** for Web data extracting.

## Installation

```
pip install data-extractor
```

## Usage

Download RSS Sample file

```
wget http://www.rssboard.org/files/sample-rss-2.xml
```

### Simple Extractor

```python
import json

from pathlib import Path

from data_extractor.item import Field, Item
from lxml.etree import fromstring


root = fromstring(Path("sample-rss-2.xml").read_text())
```

Using `XPathExtractor` to extract rss channel title

```python
from data_extractor.lxml import XPathExtractor


XPathExtractor("//channel/title/text()").extract_first(root)
# 'Liftoff News'
```

Using `TextCSSExtractor` to extract all rss item link

```python
from data_extractor.lxml import TextCSSExtractor


TextCSSExtractor("item>link").extract(root)
# ['http://liftoff.msfc.nasa.gov/news/2003/news-starcity.asp',
#  'http://liftoff.msfc.nasa.gov/news/2003/news-VASIMR.asp',
#  'http://liftoff.msfc.nasa.gov/news/2003/news-laundry.asp']
```

Using `AttrRSSExtractor` to extract rss version

```python
from data_extractor.lxml import AttrCSSExtractor


AttrCSSExtractor("rss", attr="version").extract_first(root)
# '2.0'
```


### Complex Extractor

Defining `ChannelItem` and `Channel` class, then extracting the data

```python
import json

from pathlib import Path

from data_extractor.item import Field, Item
from data_extractor.lxml import XPathExtractor

from lxml.etree import fromstring


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
```

Extracting the rss data from file

```python
root = fromstring(Path("sample-rss-2.xml").read_text())
rv = Channel(XPathExtractor("//channel")).extract(root)
print(json.dumps(rv, indent=2))
```

Output:

```json
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
```

Or just extracting the channel item from file

```python
root = fromstring(Path("sample-rss-2.xml").read_text())
rv = ChannelItem(XPathExtractor("//channel/item"), is_many=True).extract(root)
print(json.dumps(rv, indent=2))
```

Output:

```json
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
```
