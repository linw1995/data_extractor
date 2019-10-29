# Standard Library
from unittest import mock

# Third Party Library
import pytest


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
