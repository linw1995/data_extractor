# Standard Library
import inspect
import textwrap

# Third Party Library
import pytest

# First Party Library
from data_extractor.exceptions import ExtractError
from data_extractor.item import Field, Item
from data_extractor.json import JSONExtractor
from data_extractor.lxml import XPathExtractor


def test_exception_trace(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        name = Field(JSONExtractor("name"))
        gender = Field(JSONExtractor("gender"))

    class UserResponse(Item):
        start = Field(JSONExtractor("start"), default=0)
        size = Field(JSONExtractor("size"))
        total = Field(JSONExtractor("total"))
        data = User(JSONExtractor("users[*]"), is_many=True)

    extractor = UserResponse(JSONExtractor("data"))
    with pytest.raises(ExtractError) as catch:
        extractor.extract(data)

    exc = catch.value
    assert len(exc.extractors) == 3
    assert exc.extractors[0] is User.gender
    assert exc.extractors[1] is UserResponse.data
    assert exc.extractors[2] is extractor
    assert exc.element == {"id": 3, "name": "Janine Gross"}

    assert (
        str(exc.args[0])
        == textwrap.dedent(
            """
            ExtractError(Field(JSONExtractor('gender'), default=sentinel, is_many=False), element={'id': 3, 'name': 'Janine Gross'})
            |-UserResponse(JSONExtractor('data'), default=sentinel, is_many=False)
              |-User(JSONExtractor('users[*]'), default=sentinel, is_many=True)
                |-Field(JSONExtractor('gender'), default=sentinel, is_many=False)
                  |-{'id': 3, 'name': 'Janine Gross'}
            """
        ).strip()
    )


def test_field_name_overwrite_item_parameter():
    with pytest.raises(SyntaxError) as catch:

        class Parameter(Item):
            name = Field(XPathExtractor("./span[@class='name']"))
            default = Field(XPathExtractor("./span[@class='default']"))

    exc = catch.value
    assert exc.filename == __file__
    assert exc.lineno == inspect.currentframe().f_lineno - 4
    assert exc.offset == 12
    assert exc.text == "default = Field(XPathExtractor(\"./span[@class='default']\"))"
