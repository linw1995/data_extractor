# Standard Library
import os

from pathlib import Path

# Third Party Library
import nox

nox.options.stop_on_first_error = True


pythons = ["3.7", "3.8", "3.9"]

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
os.environ.pop("PYTHONPATH", None)


@nox.session(python=pythons, reuse_venv=True)
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
    session.run(
        "pdm",
        "sync",
        "-v",
        "-s",
        "test",
        *(("-s", extractor_backend) if extractor_backend else tuple()),
        external=True,
    )
    session.run("pytest", "-vv", "--cov=data_extractor", "--cov-append")


@nox.session(python=pythons, reuse_venv=True)
def coverage_report(session):
    session.run("pdm", "sync", "-v", "-ds", "test", external=True)
    session.run("coverage", "report")
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.log(
        f">> open file:/{(Path() / 'htmlcov/index.html').absolute()} to see coverage"
    )


@nox.session(reuse_venv=True)
def build_readme(session):
    session.run("pdm", "sync", "-v", "-ds", "build_readme", external=True)
    session.run(
        "python", "scripts/build_readme.py", "README.template.rst", "README.rst"
    )
