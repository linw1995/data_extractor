# Standard Library
from typing import List

# Third Party Library
import pytest

from _pytest.nodes import Node

xfail = ("item_in-place_extracting",)


def pytest_collection_modifyitems(config, items: List[Node]):
    for item in items:
        if item.name in xfail:
            item.add_marker(pytest.mark.xfail(strict=True))
