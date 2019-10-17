all: test

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

POETRY_VERSION = 0.12.17
POETRY_EXTRAS = linting test docs
POETRY_EXTRAS_ARGS = $(if $(POETRY_EXTRAS),-E,) $(subst $(SPACE),$(SPACE)-E$(SPACE),$(POETRY_EXTRAS))

init_by_venv:
	@echo ">> initing by venv..."
	@echo ">> creating venv..."
	@python3.7 -m venv .venv
	@echo ">> installing Poetry ${POETRY_VERSION}"
	@.venv/bin/pip install poetry==$(POETRY_VERSION)
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@.venv/bin/poetry install $(POETRY_EXTRAS_ARGS)
	@echo ">> all dependencies installed completed! please execute below command for development"
	@echo "> source .venv/bin/acitvate"

init_by_poetry:
	@echo ">> initing by `poetry --version`..."
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@poetry install $(POETRY_EXTRAS_ARGS)
	@echo ">> make a symlink from the env created by poetry to ./.venv"
	@[ -h .venv ] && unlink .venv && echo ">> remove old link" || true
	@poetry run sh -c "printenv VIRTUAL_ENV" | { \
		read VIRTUAL_ENV; \
		echo ">> link .venv -> $$VIRTUAL_ENV"; \
		ln -s $$VIRTUAL_ENV .venv; \
	}
	@echo ">> all dependencies installed completed! please execute below command for development"
	@echo "> poetry shell"
	@echo ">> or:"
	@echo "> source .venv/bin/acitvate"


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
