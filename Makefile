all: test

init:
	python3.7 -m virtualenv .venv
	.venv/bin/python -m pip install -U pip poetry
	.venv/bin/poetry install -E linting -E test -E docs
	@echo "init completed! please execute below command for development"
	@echo "source .venv/bin/acitvate"

isort:
	@pre-commit run isort

check-isort:
	@pre-commit run check-isort

flake8:
	@pre-commit run flake8

black:
	@pre-commit run black

check-black:
	@pre-commit run check-black

mypy:
	@pre-commit run mypy --hook-stage push

doc8:
	@pre-commit run doc8

blacken-docs:
	@pre-commit run blacken-docs

check:
	@pre-commit run --hook-stage push
check-all:
	@pre-commit run --all-files --hook-stage push

format-code: isort flake8 black blacken-docs
fc: format-code

test: check
	pytest -q -x --ff --nf

vtest: check
	pytest -vv -x --ff --nf

_cov:
	@pytest -vv --cov=data_extractor
	@coverage html
	@echo "open file://`pwd`/htmlcov/index.html to see coverage"

cov: check _cov

clean:
	@rm -f .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist

.PHONY: all check check_isort check_black fc flake8 black blaken-docs isort init mypy test vtest _cov cov clean doc8
