all: test

isort: .isort

.isort:
	isort -rc data_extractor tests docs/source/conf.py
	@touch .isort

check_isort: .check_isort

.check_isort:
	isort -rc -c data_extractor tests docs/source/conf.py
	@touch .check_isort

flake: .flake

.flake:
	flake8 data_extractor tests docs/source/conf.py
	@touch .flake

black: .black

.black:
	black data_extractor tests docs/source/conf.py
	@touch .black

check_black: .check_black

.check_black:
	black --check data_extractor tests docs/source/conf.py
	@touch .check_black

mypy: .mypy

.mypy:
	mypy data_extractor
	@touch .mypy

doc8: .doc8

.doc8:
	doc8 docs/source
	@touch .doc8

check: .check

.check: .check_isort .check_black .flake

check_all: .check_all

.check_all: .check mypy doc8

format_code: .format_code
fc: .format_code

.format_code: .isort .black

test: .check
	pytest -q -x --ff --nf

vtest: .check
	pytest -vv -x --ff --nf

_cov:
	pytest -vv --cov=data_extractor
	coverage html
	@echo "open file://`pwd`/htmlcov/index.html to see coverage"

cov: .check _cov

clean:
	@rm -f .black
	@rm -f .coverage
	@rm -f .check_isort
	@rm -f .check_black
	@rm -f .flake
	@rm -f .isort
	@rm -f .mypy
	@rm -f .doc8
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist

.PHONY: all check check_isort check_black fc flake black isort mypy test vtest _cov cov clean doc8
