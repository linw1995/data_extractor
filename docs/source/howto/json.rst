=================
Extract JSON Data
=================

The function to extract data from the JSON file
powered by python-jsonpath-rw_ and python-jsonpath-rw-ext_
to support JSONPath_.

Use the :class:`data_extractor.json.JSONExtractor` to extract data.

.. code-block:: python3

    import json
    from data_extractor import JSONExtractor

    text = '{"foo": [{"baz": 1}, {"baz": 2}]}'
    data = json.loads(text)
    assert JSONExtractor("foo[*].baz").extract(data) == [1, 2]

.. _python-jsonpath-rw: https://github.com/kennknowles/python-jsonpath-rw
.. _python-jsonpath-rw-ext: https://python-jsonpath-rw-ext.readthedocs.org/en/latest/
.. _JSONPath: https://goessner.net/articles/JsonPath/
