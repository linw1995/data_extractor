# Standard Library
from typing import Any

# Third Party Library
import pytest

from typing_extensions import get_args

# First Party Library
from data_extractor.item import Field

# Local Folder
from .utils import D


@pytest.mark.xfail(msg="cant set Any as a default args of Generic Field")
def test_field_with_default_typing():
    assert get_args(Field) == (Any,)


def test_field_with_type():
    StrField = Field[str]
    assert get_args(StrField) == (str,)
    f = StrField(D())
    assert f.type is str
    assert f.extract(1) == "1"


def test_field_with_convertor():
    f = Field(D(), convertor=lambda x: str(x).upper())
    assert f.type is None
    assert f.extract("abc") == "ABC"
    f = Field(D(), type=str, convertor=lambda x: str(x).upper())
    assert f.type is str
    assert f.extract("abc") == "ABC"
