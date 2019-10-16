# History

## v0.4.1

- d180992 Add pre-commit support and fix pre-commit check error (#32)
- bd680c1 Update pyproject.toml
- 64f30f7 remove unhappened condtional

## v0.4.0

- 74f569b Update docs and lint docs (#31)
- 4188634 Support RTD (#30)
- a5b776f Separate dependencies (#29)
- 69079b4 Generate simple extractor from a complex extractor (#28)
- 58a7570 Support JSONPath ext syntax (#26)
- bb7c602 Replace Pipenv with Poetry (#24)

## v0.3.2

- cd65ad0 Make Parameter extractor Optional

## v0.2.2

- fca801a Merge pull request #22 from linw1995/hotfix
  - 8bf2a62 Fix name overwritten syntax checking that includes the `__init__` first parameter.
  - 10e2ca0 Fix raise wrong execption from python repl, oneline code or type() creation.

## v0.2.1

- a05b75f Export all from the root module.
- d2900d3 Add Optional Parameter name for special field name. (#19)
- 99a4a7f Raise SyntaxError when the field name is the same as Item's parameter… (#18)

## v0.2.0

- 9c2e2cd Rename ExtractFirstMixin into SimpleExtractorBase (#12)
- bac925d Raise ValueError when misplaced the complex extractor in complex extractor. (#13)
- 88b9227 Wrap expr exception (#14)
- aeb9520 Deploy Docs on GitHub Pages. (#15)
  - Update docstring.
  - Deploy Docs on Github Pages.
  - Add Quickstarts.rst
- Bump into beta

## v0.1.5

- cabfac3 Add utils.py
- 9e1c005 Make all extractor class inherit the same ABC.
- 7828a1a Make easy to trace exception thrown by complex extractor extracting data.

## v0.1.4

- f4267fe Modify docstr
- 6f2f8d1 Add more docstr

## v0.1.3

- 5f4b0e0 Update README.md
- 1b8bfb9 Add UserWarning when extractor can't extract first item from result
- dd2cd25 Remove the useless _extract call
- 655ec9d Add UserWarning when expr is conflict with parameter is_many=True
- bcade2c No alow user to set is_many=True and default!=sentinel at same time
- 761bd30 Add more unit tests

## v0.1.2

- Add exceptions.py and ExprError
- Change travis-ci deploy stage condition
- Add travis-ci deploy github release

## v0.1.1

- Rename `.html` to `.lxml`; Remove `fromstring`, `tostring` function from `.lxml`
  - Rename .html to .lxml
  - use `lxml.html.fromstring` and `lxml.html.tostring` to process HTML
  - use `lxml.etree.fromstring` and `lxml.etree.tostring` to process XML
- Add **check_isort**, **check_black**, **check**, **check_all**, **fc**: **format_code** into Makefile for development.

## v0.1.0

- initialize project
- add Extractor to extract data from the text which format is HTML or JSON.
- add complex extractor: Field, Item
