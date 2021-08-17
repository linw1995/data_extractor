=========
Changelog
=========

v0.10.2
~~~~~~~

**Build**

- upgrade jsonpath-extractor to v0.8.0

v0.10.1
~~~~~~~

**Fix**

- typo in .utils.Property

v0.10.0
~~~~~~~~~~

**Feature**

- supports PEP 561 -- Distributing and Packaging Type Information

**Fix**

- remove LICENSE file from dist files
- duplicated extracting if class attrs overlap happened #67
- remove super class sub-extractors error #68

**Refactor**

- remove duplciated module "data_extractor.abc"
- remove the lazy build mechanism of extractors
- JSON backend invoking mechanism
- make all properties of extractors immutable

**Document**

- fix wrong docstring of "data_extractor.utils.Property"

.. include:: history.rst
    :start-line: 4
