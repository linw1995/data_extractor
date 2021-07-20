# First Party Library
from data_extractor.core import AbstractSimpleExtractor


class DumyExtractor(AbstractSimpleExtractor):
    def __init__(self, expr=""):
        super().__init__(expr)

    def extract(self, element):
        return [element]


D = DumyExtractor
