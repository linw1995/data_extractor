# Third Party Library
import pytest

# First Party Library
import data_extractor.json

from data_extractor.exceptions import ExtractError
from data_extractor.item import AutoItem, Field
from data_extractor.json import JSONExtractor

# Local Folder
from .utils import is_built

StrField = Field[str]


def test_no_needed_packages():
    data_extractor.json.json_extractor_backend = None
    with pytest.raises(RuntimeError):
        JSONExtractor()


@pytest.mark.usefixtures("json_extractor_backend")
def test_exception_trace(json0, build_first):
    data = json0

    class User(AutoItem):
        uid = StrField(JSONExtractor("id"))
        username = StrField(JSONExtractor("name"), name="name")
        gender = StrField(JSONExtractor("gender"))

    class UserResponse(AutoItem):
        start = StrField(JSONExtractor("start"), default=0)
        size = StrField(JSONExtractor("size"))
        total = StrField(JSONExtractor("total"))
        data = User(JSONExtractor("users[*]"), is_many=True)

    extractor = UserResponse(JSONExtractor("data"))
    assert not is_built(extractor)
    assert not is_built(extractor.extractor)
    if build_first:
        extractor.build()
        assert is_built(extractor)
        assert is_built(extractor.extractor)

    with pytest.raises(ExtractError) as catch:
        extractor.extract(data)

    assert is_built(extractor)
    assert is_built(extractor.extractor)

    exc = catch.value
    assert len(exc.extractors) == 3
    assert exc.extractors[0] is User.gender
    assert exc.extractors[1] is UserResponse.data
    assert exc.extractors[2] is extractor
    assert exc.element == {"id": 3, "name": "Janine Gross"}

    assert (
        str(exc.args[0])
        == """
ExtractError(Field(JSONExtractor('gender')), element={'id': 3, 'name': 'Janine Gross'})
|-UserResponse(JSONExtractor('data'))
  |-User(JSONExtractor('users[*]'), is_many=True)
    |-Field(JSONExtractor('gender'))
      |-{'id': 3, 'name': 'Janine Gross'}
    """.strip()
    )
