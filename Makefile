ifneq ($(shell [ -f ./.venv/bin/python ] && echo 1),1)

all:

install-deps: $(shell find Pipfile -type f)
	python3 -m virtualenv .venv
	.venv/bin/python -m pip install -U pip pipenv
	.venv/bin/pipenv install --dev --deploy

install-deps-without-dev: $(shell find Pipfile -type f)
	python3 -m virtualenv .venv
	.venv/bin/python -m pip install -U pip pipenv
	.venv/bin/python install --deploy

%:
	@echo "virtualenv missing! Please execute:"
	@echo "make install-deps"
	@exit 1

else

ifneq ($(shell ./.venv/bin/python -c "import sys;print(sys.executable)"),$(shell which python))

all:

%:
	@echo "virtualenv deactivated! Please execute:"
	@echo "source ./.venv/bin/acitvate"
	@exit 1

else

all: test

isort: .isort

.isort: $(shell find data_extractor -type d) \
		$(shell find tests -type d)
	isort -rc data_extractor tests
	@touch .isort

check_isort: .check_isort

.check_isort: $(shell find data_extractor -type d) \
		      $(shell find tests -type d)
	isort -rc -c data_extractor tests
	@touch .check_isort

flake: .flake

.flake: $(shell find data_extractor -type d) \
		$(shell find tests -type d)
	flake8 data_extractor tests
	@touch .flake

black: .black

.black: $(shell find data_extractor -type d) \
		$(shell find tests -type d)
	black data_extractor tests
	@touch .black

check_black: .check_black

.check_black: $(shell find data_extractor -type d) \
		      $(shell find tests -type d)
	black --check data_extractor tests
	@touch .check_black

mypy: .mypy

.mypy: $(shell find data_extractor -type d)
	mypy data_extractor
	@touch .mypy

check: .check

.check: $(shell find data_extractor -type d) \
		$(shell find tests -type d) \
		.check_isort .check_black .flake

check_all: .check_all

.check_all: $(shell find data_extractor -type d) \
		$(shell find tests -type d) \
		.check mypy

format_code: .format_code
fc: .format_code

.format_code: $(shell find data_extractor -type d) \
		      $(shell find tests -type d) \
			  .isort .black

test: .check
	pytest -q -x --ff --nf

vtest: .check
	pytest -vv -x --ff --nf

cov: .check
	pytest -vv --cov=data_extractor
	coverage html
	@echo "open file://`pwd`/htmlcov/index.html to see coverage"

clean:
	@rm -f .black
	@rm -f .coverage
	@rm -f .check_isort
	@rm -f .check_black
	@rm -f .flake
	@rm -f .isort
	@rm -f .mypy
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist

build:
	python setup.py sdist bdist_wheel


.PHONY: all check check_isort check_black fc flake black isort mypy test vtest cov clean build

endif
endif
