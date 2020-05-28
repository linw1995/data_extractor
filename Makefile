all: test

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

POETRY_VERSION = 1.0.0
POETRY_EXTRAS = lint test docs jsonpath-rw jsonpath-rw-ext jsonpath-extractor
POETRY_EXTRAS_ARGS = $(if $(POETRY_EXTRAS),-E,) $(subst $(SPACE),$(SPACE)-E$(SPACE),$(POETRY_EXTRAS))

deinit:
	@echo ">> remove venv..."
	@[ -h .venv ] && rm -rf `realpath .venv` && rm .venv && echo ">> remove success" || true
	@[ -d .venv ] && rm -rf .venv && echo ">> remove success" || true

init_by_venv:
	@echo ">> initing by venv..."
	@echo ">> creating venv..."
	@python3 -m virtualenv .venv
	@echo ">> installing Poetry ${POETRY_VERSION}"
	@.venv/bin/pip install poetry==$(POETRY_VERSION)
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@.venv/bin/poetry -v install $(POETRY_EXTRAS_ARGS)
	@echo ">> all dependencies installed completed! please execute below command for development"
	@echo "> source .venv/bin/acitvate"

init_by_poetry:
	@echo ">> initing by `poetry --version`..."
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@poetry install -v $(POETRY_EXTRAS_ARGS)
	@echo ">> make a symlink from the env created by poetry to ./.venv"
	@[ -h .venv ] && unlink .venv && echo ">> remove old link" || true
	@poetry run python -c "import sys; print(sys.prefix)" | { \
		read PYTHON_PREFIX; \
		echo ">> link .venv -> $$PYTHON_PREFIX"; \
		ln -s $$PYTHON_PREFIX .venv; \
		ln -s `which poetry` .venv/bin/poetry >/dev/null 2>&1 || true; \
	}
	@echo ">> all dependencies installed completed! please execute below command for development"
	@echo "> poetry shell"
	@echo ">> or:"
	@echo "> source .venv/bin/acitvate"


isort:
	@.venv/bin/pre-commit run isort

check-isort:
	@.venv/bin/pre-commit run check-isort

flake8:
	@.venv/bin/pre-commit run flake8

black:
	@.venv/bin/pre-commit run black

check-black:
	@.venv/bin/pre-commit run check-black

mypy:
	@.venv/bin/pre-commit run mypy --hook-stage push

doc8:
	@.venv/bin/pre-commit run doc8

blacken-docs:
	@.venv/bin/pre-commit run blacken-docs

check:
	@.venv/bin/pre-commit run --hook-stage push
check-all:
	@.venv/bin/pre-commit run --all-files --hook-stage push

format-code: isort black blacken-docs
fc: format-code

_stash:
	@git diff > unstaged.diff && \
		if [ -s unstaged.diff ]; then \
			echo ">> Stashing into unstaged.diff"; \
			git apply -R unstaged.diff; \
		else \
			rm unstaged.diff; \
		fi;

_unstash:
	@if [ -s unstaged.diff ]; then \
		echo ">> Recovering from unstaged.diff"; \
		git apply unstaged.diff && \
		rm unstaged.diff; \
	fi;

_finally=|| code=$$?; \
	make _unstash \
		&& exit $$code

_test:
	@.venv/bin/pytest -q -x --ff --nf

test: _stash
	@make _test $(_finally)

_vtest:
	@.venv/bin/pytest -vv -x --ff --nf

vtest: _stash
	@make _vtest $(_finally)

_cov:
	@.venv/bin/pytest -vv --cov=data_extractor
	@.venv/bin/coverage xml
	@.venv/bin/coverage html
	@echo ">> open file://`pwd`/htmlcov/index.html to see coverage"

cov: _stash
	@make _cov $(_finally)

_nox:
	@rm -f .coverage
	@.venv/bin/nox
	@.venv/bin/coverage xml
	@.venv/bin/coverage html
	@echo ">> open file://`pwd`/htmlcov/index.html to see coverage"

nox: _stash
	@make _nox $(_finally)

export_requirements_txt:
	@.venv/bin/nox -k export_requirements_txt

export: export_requirements_txt

pre-commit_init:
	@.venv/bin/pre-commit install

clean:
	@rm -f .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist

.PHONY: all check check_isort check_black fc flake8 black blaken-docs isort init mypy nox \
		test vtest _cov cov clean doc8 export_requirements_txt export pre-commit_init
