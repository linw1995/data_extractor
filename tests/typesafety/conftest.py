# Standard Library
from typing import List

# Third Party Library
import pytest

from _pytest.nodes import Node

xfail: List[str] = []


def pytest_collection_modifyitems(config, items: List[Node]):
    for item in items:
        if item.name in xfail:
            item.add_marker(pytest.mark.xfail(strict=True))
