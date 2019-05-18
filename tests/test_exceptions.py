# Standard Library
import textwrap

# Third Party Library
import pytest

# First Party Library
from data_extractor.exceptions import ExtractError
from data_extractor.item import Field, Item
from data_extractor.json import JSONExtractor


def test_exception_trace(json0):
    data = json0

    class User(Item):
        uid = Field(JSONExtractor("id"))
        username = Field(JSONExtractor("name"), name="name")
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
            ExtractError(Field(JSONExtractor('gender')), element={'id': 3, 'name': 'Janine Gross'})
            |-UserResponse(JSONExtractor('data'))
              |-User(JSONExtractor('users[*]'), is_many=True)
                |-Field(JSONExtractor('gender'))
                  |-{'id': 3, 'name': 'Janine Gross'}
            """
        ).strip()
    )
