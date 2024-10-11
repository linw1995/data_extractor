# Standard Library
import os

from pathlib import Path

# Third Party Library
import nox

nox.options.stop_on_first_error = True


pythons = ["3.9", "3.10", "3.11", "3.12"]

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
os.environ.pop("PYTHONPATH", None)


def venv_setup_on_create(session, install):
    cwd = os.getcwd()
    session.cd(session.create_tmp())
    if session.run(
        "python", "-Esc", "import data_extractor", success_codes=(1, 0), silent=True
    ):
        install(session)
    session.cd(cwd)


@nox.session(python=pythons, venv_backend="venv")
@nox.parametrize(
    "extractor_backend",
    [
        None,
        "jsonpath-extractor",
        "jsonpath-rw",
        "jsonpath-rw-ext",
        "lxml",
        "cssselect",
    ],
)
def coverage_test(session, extractor_backend):
    venv_setup_on_create(
        session,
        lambda s: s.run(
            "pdm",
            "sync",
            "-v",
            "-G",
            "test",
            *(("-G", extractor_backend) if extractor_backend else tuple()),
            external=True,
        ),
    )
    session.run(
        "pytest",
        "-vv",
        "--cov=data_extractor",
        "--cov-append",
        "--ignore",
        "tests/typesafety",
        *session.posargs,
    )


@nox.session(python=pythons, venv_backend="venv")
def coverage_report(session):
    venv_setup_on_create(
        session,
        lambda s: s.run("pdm", "sync", "-v", "-G", "test", external=True),
    )
    session.run("coverage", "report")
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.log(
        f">> open file:/{(Path() / 'htmlcov/index.html').absolute()} to see coverage"
    )


@nox.session(python=pythons, venv_backend="venv")
def test_mypy_plugin(session):
    venv_setup_on_create(
        session,
        lambda s: s.run("pdm", "sync", "-v", "-G", "test-mypy-plugin", external=True),
    )

    session.run(
        "pytest",
        "-vv",
        "--cov=data_extractor/contrib/mypy",
        "--cov-append",
        "--mypy-same-process",
        "--mypy-ini-file=./tests/mypy.ini",
        "tests/typesafety",
        *(session.posargs if session.posargs else tuple()),
    )


@nox.session(python=pythons[-1:], venv_backend="venv")
def build_readme(session):
    venv_setup_on_create(
        session,
        lambda s: s.run("pdm", "sync", "-v", "-G", "build_readme", external=True),
    )
    session.run(
        "python", "scripts/build_readme.py", "README.template.rst", "README.rst"
    )
