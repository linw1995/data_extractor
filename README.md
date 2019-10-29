# Data Extractor

[![license](https://img.shields.io/github/license/linw1995/data_extractor.svg)](https://github.com/linw1995/data_extractor/blob/master/LICENSE)
[![Pypi Status](https://img.shields.io/pypi/status/data_extractor.svg)](https://pypi.org/project/data_extractor)
[![Python version](https://img.shields.io/pypi/pyversions/data_extractor.svg)](https://pypi.org/project/data_extractor)
[![Package version](https://img.shields.io/pypi/v/data_extractor.svg)](https://pypi.org/project/data_extractor)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/data-extractor.svg)](https://pypi.org/project/data_extractor)
[![GitHub last commit](https://img.shields.io/github/last-commit/linw1995/data_extractor.svg)](https://github.com/linw1995/data_extractor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://travis-ci.org/linw1995/data_extractor.svg?branch=master)](https://travis-ci.org/linw1995/data_extractor)
[![codecov](https://codecov.io/gh/linw1995/data_extractor/branch/master/graph/badge.svg)](https://codecov.io/gh/linw1995/data_extractor)
[![Documentation Status](https://readthedocs.org/projects/data-extractor/badge/?version=latest)](https://data-extractor.readthedocs.io/en/latest/?badge=latest)

Combine **XPath**, **CSS Selectors** and **JSONPath** for Web data extracting.

## Changelog

### v0.5.0

- 0056f37 Split AbstractExtractor into AbstractSimpleExtractor and AbstractComplexExtractor
- c42aeb5 Feature/more friendly development setup (#34)
- 2f9a71c New:Support testing in 3.8
- c8bd593 New:Stash unstaged code before testing
- d2a18a8 New:Best way to raise new exc
- 90fa9c8 New:ExprError `__str__` implementation
- d961768 Fix:Update mypy pre-commit config
- e5d59c3 New:Raise SyntaxError when field overwrites method (#38)
