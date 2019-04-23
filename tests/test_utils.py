# First Party Library
from data_extractor.utils import LazyStr


def test_lazy_str():
    string = ""

    def func():
        nonlocal string
        return string

    ls = LazyStr(func=func)
    assert str(ls) == ""

    string = "abc"
    assert str(ls) == "abc"
