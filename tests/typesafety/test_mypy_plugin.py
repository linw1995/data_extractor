# Standard Library
from typing import Any, cast

# Third Party Library
from mypy.options import Options
from mypy.types import AnyType, TypeOfAny

# First Party Library
from data_extractor.contrib.mypy import DataExtractorPlugin


class NewTypedDictAnalyzer:
    def build_typeddict_typeinfo(self, *args: Any) -> object:
        if isinstance(args[1], list):
            raise TypeError("old signature unsupported")

        return args


def test_build_typeddict_typeinfo_supports_readonly_keys_api():
    plugin = DataExtractorPlugin(Options())
    value_type = AnyType(TypeOfAny.special_form)

    result = plugin.build_typeddict_typeinfo(
        cast(Any, NewTypedDictAnalyzer()),
        "Result",
        ["value"],
        [value_type],
    )

    assert result == ("Result", {"value": value_type}, {"value"}, set(), -1, None)
