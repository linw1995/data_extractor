=======
History
=======

v0.9.0
~~~~~~

**Fix**

- type annotations #63 #64

**Refactor**

- .utils.Property with "Customized names" support #64
- rename .abc to .core and mark elder duplciated #65

v0.8.0
~~~~~~

- 11bfd2c supports latest jsonpath-extractor package

v0.7.0
~~~~~~

- 65d1fce Fix:Create JSONExtractor with wrong subtype
- 407cd78 New:Make lxml and cssselect optional (#61)

v0.6.1
~~~~~~

- d28fff4 Fix:Item created error by ``type`` function. (Issue #56)

v0.6.0
~~~~~~

- f1d21fe New:Make different implementations of JSONExtractor optional
- 0175cde New:Add jsonpath-extractor as opitional json extractor backend
- 3b6da8b Chg:Upgrade dependencies

v0.6.0-alpha.3
~~~~~~~~~~~~~~

- 1982302 Fix:Type annotation error

v0.6.0.dev2
~~~~~~~~~~~

- b7edbae Dev,New:Use nox test in multi-py-versions, Update workflow
- a043838 Fix:Can't import JSONPathExtractor from root module
- a23ece9 Test,Fix:Missing JSONPathExtractor in simple extractor tests
- 5903ff9 Dev,Fix:Nox changes symlink '.venv' of virtualenv of development
- 57d03ad Dev,Fix:Install unneeded development dependencies

v0.6.0.dev1
~~~~~~~~~~~

- 2459f7d Dev,New:Add Github Actions for CI
- a151a91 Dev,New:Add scripts/export_requirements_txt.sh
- f7cdaa3 Dev,Chg:Remove travis-ci
- f1d21fe New:Make different implementations of JSONExtractor optional
- 9f74619 Fix:Use __getattr__ on the module in the wrong way
- 25a8bf8 Dev,Fix:Cannot use pytest.mark.usefixtures() in pytest.param
- 8f51603 Dev,Chg:Upgrade poetry version in Makefile
- 21aa08e Dev,Chg:Test in two ways
- 4cb4678 Chg:Upgrade dependencies
- 4177b98 Dev,Fix:remove the venv before pretest installation
- 0175cde New:Add jsonpath-extractor as opitional json extractor backend

v0.5.4
~~~~~~

- 9552c79 Fix:Simplified item's extract_first method fail to raise ExtractError
- 08167ab Fix:Simplified item's extract_first method
  should support param default
- 6e4c269 New:More unittest for testing the simplified items
- a35b85a Chg:Update poetry.lock
- e5ff37b Docs,Chg:Update travis-ci status source in the README.rst

v0.5.3
~~~~~~

- 6a26be5 Chg:Wrap the single return value as a list
- 0b63927 Fix:Item can not extract the data is list type
- 9deeb5f Chg:Update poetry.lock

v0.5.2
~~~~~~

- 0561672 Fix:Wrong parameter name

v0.5.1
~~~~~~

- c9b07f4 Fix:Wrong shield placing
- b198712 Dev,Fix:Build travis-ci config validation

v0.5.0
~~~~~~

- 0056f37 Split AbstractExtractor into AbstractSimpleExtractor and
  AbstractComplexExtractor
- c42aeb5 Feature/more friendly development setup (#34)
- 2f9a71c New:Support testing in 3.8
- c8bd593 New:Stash unstaged code before testing
- d2a18a8 New:Best way to raise new exc
- 90fa9c8 New:ExprError ``__str__`` implementation
- d961768 Fix:Update mypy pre-commit config
- e5d59c3 New:Raise SyntaxError when field overwrites method (#38)
- 7720fb9 Feature/avoid field overwriting (#39)
- b722717 Dev,Fix:Black configure not working
- f8f0df8 New:Implement extractors' build method
- 98ada74 Chg:Update docs

v0.4.1
~~~~~~

- d180992 Add pre-commit support and fix pre-commit check error (#32)
- bd680c1 Update pyproject.toml
- 64f30f7 remove unhappened condtional

v0.4.0
~~~~~~

- 74f569b Update docs and lint docs (#31)
- 4188634 Support RTD (#30)
- a5b776f Separate dependencies (#29)
- 69079b4 Generate simple extractor from a complex extractor (#28)
- 58a7570 Support JSONPath ext syntax (#26)
- bb7c602 Replace Pipenv with Poetry (#24)

v0.3.2
~~~~~~

- cd65ad0 Make Parameter extractor Optional

v0.2.2
~~~~~~

- fca801a Merge pull request #22 from linw1995/hotfix

  + 8bf2a62 Fix name overwritten syntax checking
    that includes the ``__init__`` first parameter.

  + 10e2ca0 Fix raise wrong execption from python repl,
    oneline code or type() creation.

v0.2.1
~~~~~~

- a05b75f Export all from the root module.
- d2900d3 Add Optional Parameter name for special field name. (#19)
- 99a4a7f Raise SyntaxError
  when the field name is the same as Item's parameter… (#18)

v0.2.0
~~~~~~

- 9c2e2cd Rename ExtractFirstMixin into SimpleExtractorBase (#12)
- bac925d Raise ValueError
  when misplaced the complex extractor in complex extractor. (#13)

- 88b9227 Wrap expr exception (#14)
- aeb9520 Deploy Docs on GitHub Pages. (#15)

  + Update docstring.
  + Deploy Docs on Github Pages.
  + Add Quickstarts.rst

- Bump into beta

v0.1.5
~~~~~~

- cabfac3 Add utils.py
- 9e1c005 Make all extractor class inherit the same ABC.
- 7828a1a Make easy to trace exception thrown
  by complex extractor extracting data.

v0.1.4
~~~~~~

- f4267fe Modify docstr
- 6f2f8d1 Add more docstr

v0.1.3
~~~~~~

- 5f4b0e0 Update README.md
- 1b8bfb9 Add UserWarning when extractor can't extract first item from result
- dd2cd25 Remove the useless _extract call
- 655ec9d Add UserWarning when expr is conflict with parameter is_many=True
- bcade2c No alow user to set is_many=True and default!=sentinel at same time
- 761bd30 Add more unit tests

v0.1.2
~~~~~~

- Add exceptions.py and ExprError
- Change travis-ci deploy stage condition
- Add travis-ci deploy github release

v0.1.1
~~~~~~

- Rename ``.html`` to ``.lxml``;
  Remove ``fromstring``, ``tostring`` function from ``.lxml``

  + Rename .html to .lxml
  + use ``lxml.html.fromstring`` and ``lxml.html.tostring`` to process HTML
  + use ``lxml.etree.fromstring`` and ``lxml.etree.tostring`` to process XML

- Add check_isort, check_black, check,
  check_all, fc: format_code into Makefile for development.

v0.1.0
~~~~~~

- initialize project
- add Extractor to extract data from the text which format is HTML or JSON.
- add complex extractor: Field, Item
