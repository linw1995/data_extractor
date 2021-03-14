# First Party Library
from data_extractor.core import AbstractExtractors, AbstractSimpleExtractor


def is_built(obj: AbstractExtractors = None) -> bool:
    return obj is not None and obj.built


class DumyExtractor(AbstractSimpleExtractor):
    def __init__(self, expr=""):
        super().__init__(expr)

    def extract(self, element):
        return [element]

    def build(self):
        pass


D = DumyExtractor
