help:
	@echo "PYTHON=X.Y init		setup development environemnt with specific Python version"
	@echo "init			setup development environment with defualt Python version 3.11"
	@echo "update-dev		update devepoment dependencies via pdm and via pre-commit"
	@echo "update			update all dependencies via pdm and via pre-commit"
	@echo "pre-commit		setup git hooks"
	@echo "check-all		run code quality checkers"
	@echo "test			run quick tests"
	@echo "vtest			run quick tests with verbose"
	@echo "PYTHON=X.Y cov		run tests with coverage and with specific Python version"
	@echo "cov			run tests with coverage and with default Python version 3.11"
	@echo "test-mypy-plugin	run mypy plugin tests"
	@echo "type-check		run static type checking"

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

PYTHON = 3.13
EXTRAS = lxml cssselect jsonpath-extractor jsonpath-rw jsonpath-rw-ext
DEV_EXTRAS = test test-mypy-plugin docs
EXTRAS_ARGS = $(if $(EXTRAS),-G,) $(subst $(SPACE),$(SPACE)-G$(SPACE),$(EXTRAS))
DEV_EXTRAS_ARGS = $(if $(DEV_EXTRAS),-G,) $(subst $(SPACE),$(SPACE)-G$(SPACE),$(DEV_EXTRAS))

# Environment setup
init:
	@echo ">> installing $(if $(EXTRAS),\"$(EXTRAS)\" ,)$(if $(DEV_EXTRAS),\"$(DEV_EXTRAS)\" ,)dependencies by pdm"
	$(if $(PYTHON),pdm use -f $(PYTHON),)
	pdm info && pdm info --env
	pdm install $(EXTRAS_ARGS) $(DEV_EXTRAS_ARGS)
	pdm config -l python.use_venv true

deinit:
	rm -rf .nox
	rm -rf __pypackages__
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf *.egg-info

update-dev:
	pdm update $(DEV_EXTRAS_ARGS) $(EXTRAS_ARGS)
	pre-commit autoupdate

update:
	pdm update
	pre-commit autoupdate

# Environment setup end

pre-commit:
	pre-commit install --hook-type commit-msg --hook-type pre-commit --overwrite

check-all:
	pre-commit run --all-files

type-check:
	pre-commit run mypy

test:
	pdm run pytest -q -x --ff --nf --ignore tests/typesafety

vtest:
	pdm run pytest -vv -x --ff --nf --ignore tests/typesafety

test-mypy-plugin:
	rm -rf .coverage
	nox -p $(PYTHON) -s test_mypy_plugin coverage_report -- $(TARGET)

test-mypy-plugin-full:
	rm -rf .coverage
	nox -s test_mypy_plugin -- $(TARGET)
	nox -p 3.10 -s coverage_report

cov:
	rm -rf .coverage
	nox -p $(PYTHON) -s coverage_test coverage_report -- $(TARGET)

cov-full:
	rm -rf .coverage
	nox -s coverage_test -- $(TARGET)
	nox -p 3.10 -s coverage_report
