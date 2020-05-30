=================
Extract JSON Data
=================

The function to extract data from the JSON file
powered by python-jsonpath-rw_ and python-jsonpath-rw-ext_
to support JSONPath_.
Or use a new syntax of JSONPATH for extracting
by installing optional dependency jsonpath-extractor_.

Run below command to install optional dependency.

.. code-block:: shell

    pip install "data_extractor[jsonpath-rw]"
    pip install "data_extractor[jsonpath-rw-ext]"

    pip install "data_extractor[jsonpath-extractor]"

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
.. _jsonpath-extractor: https://github.com/linw1995/jsonpath

By changing :data:`json_extractor_backend`
to use a specific backend of JSON extractor.
See APIs ref of :class:`data_extractor.json.JSONExtractor`
for additional details.
