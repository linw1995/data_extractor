# Third Party Library
import pytest

# First Party Library
from data_extractor.json import JSONExtractor


@pytest.mark.usefixtures("json_extractor_backend")
@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        (
            JSONExtractor,
            {"expr": "boo"},
            {"boo": "boo"},
            "boo",
        )
    ],
)
def test_build_implicitly_by_jpath(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built


@pytest.mark.usefixtures("json_extractor_backend")
@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        (
            JSONExtractor,
            {"expr": "boo"},
            {"boo": "boo"},
            "boo",
        )
    ],
)
def test_build_explicitly_by_jpath(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    extractor.build()
    assert extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built


@pytest.mark.usefixtures("json_extractor_backend")
@pytest.mark.parametrize(
    "Extractor, kwargs, element, expect",
    [
        (
            JSONExtractor,
            {"expr": "boo"},
            {"boo": "boo"},
            "boo",
        )
    ],
)
def test_modify_built_by_jpath(Extractor, kwargs, element, expect):
    extractor = Extractor(**kwargs)
    assert not extractor.built

    extractor.build()
    assert extractor.built

    extractor.expr = kwargs["expr"]
    assert not extractor.built

    extractor.build()
    assert extractor.built

    assert extractor.extract_first(element) == expect
    assert extractor.built
