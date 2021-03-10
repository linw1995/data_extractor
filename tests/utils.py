# First Party Library
from data_extractor.core import AbstractExtractors


def is_built(obj: AbstractExtractors = None) -> bool:
    return obj is not None and obj.built
