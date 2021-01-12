# Standard Library
import platform

# Third Party Library
import nox

nox.options.stop_on_first_error = True

current_python_version = "%s.%s" % platform.python_version_tuple()[:2]


pythons = ["3.7", "3.8", "3.9"]
assert current_python_version in pythons
pythons = [current_python_version]


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
def test(session, extractor_backend):
    session.run(
        "poetry",
        "install",
        "-v",
        "-E",
        "test",
        *(("-E", extractor_backend) if extractor_backend else tuple()),
        "--no-dev",
        external=True,
    )
    session.run("pytest", "-vv", "--cov=data_extractor", "--cov-append")


@nox.session(python="3.7", reuse_venv=True)
def export_requirements_txt(session):
    session.install("poetry==1.0")
    session.install("poetry")
    session.run("python", "scripts/export_requirements_txt.py")
