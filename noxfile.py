# Standard Library
import platform

# Third Party Library
import nox


nox.options.stop_on_first_error = True

current_python_version = "%s.%s" % platform.python_version_tuple()[:2]


pythons = ["3.7", "3.8"]
assert current_python_version in pythons
pythons = [current_python_version]


@nox.session(python=pythons, reuse_venv=True)
@nox.parametrize(
    "json_extractor_backend",
    [None, "jsonpath-extractor", "jsonpath-rw", "jsonpath-rw-ext"],
)
def test(session, json_extractor_backend):
    session.run(
        "poetry",
        "install",
        "-v",
        "-E",
        "test",
        *(
            ("-E", json_extractor_backend)
            if json_extractor_backend
            else tuple()
        ),
        external=True,
    )
    session.run("pytest", "-vv", "--cov=data_extractor", "--cov-append")
