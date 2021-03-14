# Standard Library
from typing import Type

# Third Party Library
from mypy.plugin import Plugin


class DataExtractorPlugin(Plugin):
    pass


def plugin(version: str) -> Type[Plugin]:
    return DataExtractorPlugin
