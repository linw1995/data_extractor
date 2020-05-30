============
Installation
============

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
