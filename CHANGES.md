# Changelog

## v0.1.1

- Rename `.html` to `.lxml`; Remove `fromstring`, `tostring` function from `.lxml`
    * Rename .html to .lxml
    * use `lxml.html.fromstring` and `lxml.html.tostring` to process HTML
    * use `lxml.etree.fromstring` and `lxml.etree.tostring` to process XML
- Add **check_isort**, **check_black**, **check**, **check_all**, **fc**: **format_code** into Makefile for development.
