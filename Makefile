all: test

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

PYTHON = 3.9
EXTRAS = lxml cssselect jsonpath-extractor jsonpath-rw jsonpath-rw-ext test docs
EXTRAS_ARGS = $(if $(EXTRAS),-s,) $(subst $(SPACE),$(SPACE)-s$(SPACE),$(EXTRAS))

# Environment setup
init:
	@echo ">> installing $(if $(EXTRAS),\"$(EXTRAS)\" ,)dependencies by pdm"
	$(if $(PYTHON),pdm use -f $(PYTHON),)
	pdm info && pdm info --env
	pdm sync -v -d $(EXTRAS_ARGS)
	pdm config -l use_venv true

deinit:
	rm -rf .nox
	rm -rf __pypackages__
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf *.egg-info

lock: lock-deps
lock-deps:
	pdm lock -v
# Environment setup end

pre-commit:
	pre-commit install --hook-type commit-msg --hook-type pre-commit --overwrite

test:
	pdm run pytest -q -x --ff --nf

vtest:
	pdm run pytest -vv -x --ff --nf

check-all:
	pre-commit run --all-files

cov:
	rm -rf .coverage
	nox -p $(PYTHON) -s coverage_test coverage_report
