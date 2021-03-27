=========
Changelog
=========

Unreleased
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

v0.9.0
~~~~~~

**Fix**

- type annotations #63 #64

**Refactor**

- .utils.Property with "Customized names" support #64
- rename .abc to .core and mark elder duplciated #65

.. include:: history.rst
    :start-line: 4
