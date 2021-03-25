# Standard Library
import importlib.util

from unittest import mock

# Third Party Library
import pytest

# First Party Library
import data_extractor.json
import data_extractor.utils


@pytest.fixture(
    params=[
        (
            "jsonpath-extractor",
            "jsonpath",
            data_extractor.json.JSONPathExtractor,
        ),
        ("jsonpath-rw", "jsonpath_rw", data_extractor.json.JSONPathRWExtractor),
        (
            "jsonpath-rw-ext",
            "jsonpath_rw_ext",
            data_extractor.json.JSONPathRWExtExtractor,
        ),
    ],
    ids=lambda r: r[1] if r[1] else f"Missing {r[0]!r}",
)
def json_extractor_backend(request):
    package_name, module_name, backend_cls = request.param
    if not importlib.util.find_spec(module_name):
        pytest.skip(f"missing {package_name!r}")
        return

    data_extractor.json.json_extractor_backend = backend_cls
    return backend_cls


@pytest.fixture
def json0():
    return {
        "data": {
            "users": [
                {"id": 0, "name": "Vang Stout", "gender": "female"},
                {"id": 1, "name": "Jeannie Gaines", "gender": "male"},
                {"id": 2, "name": "Guzman Hunter", "gender": "female"},
                {"id": 3, "name": "Janine Gross"},
                {"id": 4, "name": "Clarke Patrick", "gender": "male"},
                {"id": 5, "name": "Whitney Mcfadden"},
            ],
            "start": 0,
            "size": 5,
            "total": 100,
        },
        "status": 0,
    }


@pytest.fixture(params=[False, True], ids=lambda x: f"stack_frame_support={x}")
def stack_frame_support(request):
    if request.param:
        yield True
    else:
        with mock.patch("inspect.currentframe") as mocked:
            mocked.return_value = None
            yield False
