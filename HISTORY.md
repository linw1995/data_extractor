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
    * Rename .html to .lxml
    * use `lxml.html.fromstring` and `lxml.html.tostring` to process HTML
    * use `lxml.etree.fromstring` and `lxml.etree.tostring` to process XML
- Add **check_isort**, **check_black**, **check**, **check_all**, **fc**: **format_code** into Makefile for development.

## v0.1.0

- initialize project
- add Extractor to extract data from the text which format is HTML or JSON.
- add complex extractor: Field, Item
