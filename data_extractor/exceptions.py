# Local Folder
from .abc import AbstractExtractor


class ExprError(Exception):
    """ Invalid Expr """

    def __init__(self, extractor: AbstractExtractor, exc: Exception):
        self.extractor = extractor
        self.exc = exc

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.extractor!r}, {self.exc!r})"


__all__ = ("ExprError",)
