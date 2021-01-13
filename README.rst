==============
Data Extractor
==============

|license| |Pypi Status| |Python version| |Package version| |PyPI - Downloads|
|GitHub last commit| |Code style: black| |Build Status| |codecov|
|Documentation Status|

Combine **XPath**, **CSS Selectors** and **JSONPath** for Web data extracting.

Quickstarts
<<<<<<<<<<<

Installation
~~~~~~~~~~~~

Install the stable version from PYPI.

.. code-block:: shell

    pip install "data-extractor[jsonpath-extractor]"  # for extracting JSON data
    pip install "data-extractor[lxml]"  # for extracting HTML data

Or install the latest version from Github.

.. code-block:: shell

    pip install "data-extractor[jsonpath-extractor] @ git+https://github.com/linw1995/data_extractor.git@master"

Extract JSON data
~~~~~~~~~~~~~~~~~

Currently supports to extract JSON data with below optional dependencies

- jsonpath-extractor_
- jsonpath-rw_
- jsonpath-rw-ext_

.. _jsonpath-extractor: https://github.com/linw1995/jsonpath
.. _jsonpath-rw: https://github.com/kennknowles/python-jsonpath-rw
.. _jsonpath-rw-ext: https://python-jsonpath-rw-ext.readthedocs.org/en/latest/

install one dependency of them to extract JSON data.

Extract HTML(XML) data
~~~~~~~~~~~~~~~~~~~~~~

Currently supports to extract HTML(XML) data with below optional dependencies

- lxml_ for using XPath_
- cssselect_ for using CSS-Selectors_

.. _lxml: https://lxml.de/
.. _XPath: https://www.w3.org/TR/xpath-10/
.. _cssselect: https://cssselect.readthedocs.io/en/latest/
.. _CSS-Selectors: https://www.w3.org/TR/selectors-3/

Usage
~~~~~

.. code-block:: python3

    from data_extractor import Field, Item, JSONExtractor


    class Count(Item):
        followings = Field(JSONExtractor("countFollowings"))
        fans = Field(JSONExtractor("countFans"))


    class User(Item):
        name_ = Field(JSONExtractor("name"), name="name")
        age = Field(JSONExtractor("age"), default=17)
        count = Count()


    assert User(JSONExtractor("data.users[*]"), is_many=True).extract(
        {
            "data": {
                "users": [
                    {
                        "name": "john",
                        "age": 19,
                        "countFollowings": 14,
                        "countFans": 212,
                    },
                    {
                        "name": "jack",
                        "description": "",
                        "countFollowings": 54,
                        "countFans": 312,
                    },
                ]
            }
        }
    ) == [
        {"name": "john", "age": 19, "count": {"followings": 14, "fans": 212}},
        {"name": "jack", "age": 17, "count": {"followings": 54, "fans": 312}},
    ]

Changelog
<<<<<<<<<

v0.8.0
~~~~~~

- 11bfd2c supports latest jsonpath-extractor package



.. |license| image:: https://img.shields.io/github/license/linw1995/data_extractor.svg
    :target: https://github.com/linw1995/data_extractor/blob/master/LICENSE

.. |Pypi Status| image:: https://img.shields.io/pypi/status/data_extractor.svg
    :target: https://pypi.org/project/data_extractor

.. |Python version| image:: https://img.shields.io/pypi/pyversions/data_extractor.svg
    :target: https://pypi.org/project/data_extractor

.. |Package version| image:: https://img.shields.io/pypi/v/data_extractor.svg
    :target: https://pypi.org/project/data_extractor

.. |PyPI - Downloads| image:: https://img.shields.io/pypi/dm/data-extractor.svg
    :target: https://pypi.org/project/data_extractor

.. |GitHub last commit| image:: https://img.shields.io/github/last-commit/linw1995/data_extractor.svg
    :target: https://github.com/linw1995/data_extractor

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. |Build Status| image:: https://github.com/linw1995/data_extractor/workflows/Lint&Test/badge.svg
    :target: https://github.com/linw1995/data_extractor/actions?query=workflow%3ALint%26Test

.. |codecov| image:: https://codecov.io/gh/linw1995/data_extractor/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/linw1995/data_extractor

.. |Documentation Status| image:: https://readthedocs.org/projects/data-extractor/badge/?version=latest
    :target: https://data-extractor.readthedocs.io/en/latest/?badge=latest
