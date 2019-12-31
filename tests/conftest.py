# Standard Library
from unittest import mock

# Third Party Library
import pytest

# First Party Library
import data_extractor.json


@pytest.fixture(
    params=[
        ("jsonpath-extractor", data_extractor.json.JSONPathExtractor),
        ("jsonpath-rw", data_extractor.json.JSONPathRWExtractor),
        ("jsonpath-rw-ext", data_extractor.json.JSONPathRWExtExtractor),
    ],
    ids=lambda r: r[1] if r[1] else f"Missing {r[0]!r}",
)
def json_extractor_backend(request):
    package_name, backend_cls = request.param
    if not backend_cls:
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


@pytest.fixture(params=[True, False], ids=lambda x: f"build_first={x!r}")
def build_first(request):
    return request.param
