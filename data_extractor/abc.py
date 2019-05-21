"""
:mod:`abc` -- Abstract Base Classes.
====================================
"""
# Standard Library
import inspect
import warnings

from abc import abstractmethod
from typing import Any, Dict, List, Tuple

# Local Folder
from .utils import sentinel


class ComplexExtractorMeta(type):
    """
    Complex Extractor Meta Class.
    """

    def __init__(cls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]):
        super().__init__(name, bases, attr_dict)
        field_names: List[str] = []

        __init_args = inspect.getfullargspec(getattr(cls, "__init__")).args

        for key, attr in attr_dict.items():
            if isinstance(type(attr), ComplexExtractorMeta):
                if key in __init_args[1:]:
                    # Item's attribute overwrites the 'Item.__init__' parameters except first parameter.
                    args = []  # type: List[Any]
                    exc_args = None
                    frame = inspect.currentframe()
                    assert (
                        frame is not None
                    ), "If running in an implementation without Python stack frame support this function returns None."
                    try:
                        outer_frame = frame.f_back

                        filename = outer_frame.f_code.co_filename
                        firstlineno = outer_frame.f_lineno
                        firstline_idx = firstlineno - 1
                        lines = None
                        try:
                            lines, _ = inspect.findsource(outer_frame)
                        except OSError:
                            # can't get the source code from python repl
                            pass

                        if lines is not None:
                            start_index = inspect.indentsize(lines[firstline_idx])
                            for lineno, line in enumerate(
                                lines[firstline_idx + 1 :], start=firstlineno + 1
                            ):
                                # iterate line in the code block body
                                cur_index = inspect.indentsize(line)
                                if cur_index <= start_index:
                                    # reach end of the code block, use code block firstlineno as SyntaxError.lineno
                                    line = lines[firstline_idx]
                                    lineno = firstlineno
                                    break

                                if line.lstrip().startswith(key):
                                    # find the line as SyntaxError.text
                                    break

                            else:
                                # reach EOF, use code block firstlineno as SyntaxError.lineno
                                line = lines[firstline_idx]
                                lineno = firstlineno

                            offset = inspect.indentsize(line)
                            line = line.strip()
                            exc_args = (filename, lineno, offset, line)
                        else:
                            line = f"{key}={attr!r}"

                    finally:
                        del outer_frame
                        del frame

                    args.append(
                        f"{line!r} overwriten the parameter {key!r} of '{name}.__init__' method. "
                        f"Please using the optional parameter name={key!r} in {attr!r} to avoid overwriting parameter name."
                    )
                    if exc_args is not None:
                        args.append(exc_args)

                    raise SyntaxError(*args)

                field_names.append(key)

        cls._field_names = field_names


class AbstractExtractor(metaclass=ComplexExtractorMeta):
    """
    All Extractors' Abstract Base Clase.

    :param expr: Extractor selector expression.
    """

    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    @abstractmethod
    def extract(self, element: Any) -> Any:
        """
        Extract data or subelement from element.

        :param element: The target data node element.

        :returns: Data or subelement.
        """
        raise NotImplementedError


class SimpleExtractorBase(AbstractExtractor):
    """
    Simple Extractor Base Class.

    :param expr: extractor selector expression.
    """

    def extract_first(self, element: Any, default: Any = sentinel) -> Any:
        """
        Extract the first data or subelement from `extract` method call result.

        :param element: The target data node element.
        :param default: Default value when not found. Default: :data:`data_extractor.utils.sentinel`.

        :returns: Data or subelement.

        :raises data_extractor.exceptions.ExtractError: Thrown by extractor extracting wrong data.
        """
        rv = self.extract(element)
        if not isinstance(rv, list):
            warnings.warn(
                f"{self!r} can't extract first item from result {rv!r}", UserWarning
            )
            return rv

        if not rv:
            if default is sentinel:
                from .exceptions import ExtractError

                raise ExtractError(self, element)

            return default

        return rv[0]


__all__ = ("AbstractExtractor", "ComplexExtractorMeta", "SimpleExtractorBase")
