"""
=====================================
:mod:`core` -- Abstract Base Classes.
=====================================
"""

# Standard Library
import ast
import inspect

from abc import abstractmethod
from collections import namedtuple
from types import FrameType, FunctionType, MethodType
from typing import Any, Dict, Optional, Tuple, Union

# Local Folder
from .utils import Property, getframe, sentinel

_LineInfo = namedtuple("_LineInfo", ["file", "lineno", "offset", "line"])


def _find_line_info_of_attr_in_source(
    frame: Optional[FrameType], key: str, attr: "AbstractComplexExtractor"
) -> _LineInfo:
    if frame is None:
        return _LineInfo(None, None, None, f"{key}={attr!r}")

    file = frame.f_code.co_filename
    firstlineno = frame.f_lineno
    firstline_idx = firstlineno - 1
    try:
        lines, _ = inspect.findsource(frame)
    except OSError:
        # can't get the source code from python repl
        return _LineInfo(None, None, None, f"{key}={attr!r}")

    start_index = inspect.indentsize(lines[firstline_idx])
    for lineno, line in enumerate(lines[firstline_idx + 1 :], start=firstlineno + 1):
        # iterate line in the code block body
        cur_index = inspect.indentsize(line)
        if cur_index <= start_index:
            # reach end of the code block,
            # use code block firstlineno as SyntaxError.lineno
            line = lines[firstline_idx]
            lineno = firstlineno
            break

        if line.lstrip().startswith(key):
            # find the line as SyntaxError.text
            break

    else:
        # reach EOF,
        # use code block firstlineno as SyntaxError.lineno
        line = lines[firstline_idx]
        lineno = firstlineno

    offset = inspect.indentsize(line)
    line = line.strip()
    return _LineInfo(file, lineno, offset, line)


def _check_field_overwrites_bases_property(
    cls: object,
    name: str,
    bases: Tuple[object],
    key: str,
    attr: "AbstractComplexExtractor",
) -> None:
    attr_from_bases = getattr(bases[-1], key, None)
    if isinstance(attr_from_bases, Property) or key == "_field_names":
        # Item's attribute overwrites its property.
        frame = getframe(2)
        exc_args = _find_line_info_of_attr_in_source(frame, key, attr)
        *_, line = exc_args
        err_msg = (
            f"{line!r} overwriten "
            f"the property {key!r} of {name}. "
            f"Please using the optional parameter name={key!r} "
            f"in {attr!r} to avoid overwriting property."
        )
        raise SyntaxError(err_msg, exc_args)


def _check_field_overwrites_bases_method(
    cls: object,
    name: str,
    bases: Tuple[object],
    key: str,
    attr: "AbstractComplexExtractor",
) -> None:
    attr_from_bases = getattr(bases[-1], key, None)
    if isinstance(attr_from_bases, (FunctionType, MethodType)):
        # Item's attribute overwrites its class bases' method.
        frame = getframe(2)
        exc_args = _find_line_info_of_attr_in_source(frame, key, attr)
        *_, line = exc_args
        err_msg = (
            f"{line!r} overwriten "
            f"the method {key!r} of {name!r}. "
            f"Please using the optional parameter name={key!r} "
            f"in {attr!r} to avoid overwriting method."
        )
        raise SyntaxError(err_msg, exc_args)


def _check_field_overwrites_method(cls: object) -> None:
    frame = getframe(2)
    if frame is None:
        return

    filename = frame.f_code.co_filename
    firstlineno = frame.f_lineno
    try:
        lines, _ = inspect.findsource(frame)
    except OSError:
        # can't get the source code from python repl
        return

    source = "".join(lines)
    mod = ast.parse(source)
    for node in ast.walk(mod):
        if isinstance(node, (ast.ClassDef, ast.Call)) and node.lineno == firstlineno:
            item_node = node
            break
    else:  # pragma: no cover
        assert 0, f"Can't find the source of {cls}."

    if isinstance(item_node, ast.Call):
        # There is no point to check if field overwrites method,
        # due to item is created by `type` function.
        return

    assigns: Dict[str, ast.Assign] = {}
    methods: Dict[str, ast.FunctionDef] = {}
    for node in item_node.body:
        if isinstance(node, ast.Assign):
            for target_ in node.targets:
                if not isinstance(target_, ast.Name):
                    continue

                assigns[target_.id] = node
        elif isinstance(node, ast.FunctionDef):
            methods[node.name] = node

    unions = assigns.keys() & methods.keys()
    if not unions:
        return

    key = next(iter(unions))
    assign = assigns[key]
    method = methods[key]
    if assign.lineno > method.lineno:
        lineno = assign.lineno
        offset = assign.col_offset
        line = lines[lineno - 1].strip()

        msg = (
            f"method {lines[method.lineno - 1].strip()!r} "
            f"on lineno={method.lineno} "
            f"overwrited by assign {line!r}. "
            f"Please using the optional parameter name={key!r} "
            f"in {line!r} to avoid overwriting."
        )
    else:
        lineno = method.lineno
        offset = method.col_offset
        line = lines[lineno - 1].strip()
        msg = (
            f"assign {lines[assign.lineno - 1].strip()!r} "
            f"on lineno={assign.lineno} "
            f"overwrited by method {line!r}. "
            f"Please using the optional parameter name={key!r} "
            f"in {lines[assign.lineno - 1].strip()!r} to avoid overwriting."
        )

    raise SyntaxError(msg, (filename, lineno, offset, line))


class SimpleExtractorMeta(type):
    """
    Simple Extractor Meta Class.
    """


class ComplexExtractorMeta(SimpleExtractorMeta):
    """
    Complex Extractor Meta Class.
    """

    def __init__(
        cls,  # noqa: B902
        name: str,
        bases: Tuple[type],
        attr_dict: Dict[str, Any],
    ):
        super().__init__(name, bases, attr_dict)

        field_names = set()
        for key, attr in attr_dict.items():
            if isinstance(type(attr), ComplexExtractorMeta):
                # can't using data_extractor.utils.is_complex_extractor here,
                # because AbstractComplexExtractor which being used in it
                # bases on ComplexExtractorMeta.
                _check_field_overwrites_bases_method(cls, name, bases, key, attr)
                _check_field_overwrites_bases_property(cls, name, bases, key, attr)

                field_names.add(key)

        # check field overwrites method
        _check_field_overwrites_method(cls)

        field_names |= set(getattr(cls, "_field_names", []))
        for key in field_names.copy():
            attr = getattr(cls, key, None)
            if not attr or not isinstance(type(attr), ComplexExtractorMeta):
                field_names.remove(key)

        cls._field_names: Tuple[str, ...] = tuple(field_names)


class AbstractSimpleExtractor(metaclass=SimpleExtractorMeta):
    """
    Abstract Simple Extractor Class.

    Its metaclass is :class:`data_extractor.core.SimpleExtractorMeta`

    :param expr: Extractor selector expression.
    :type expr: str
    """

    expr = Property[str]()

    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"

    @abstractmethod
    def extract(self, element: Any) -> Any:
        """
        Extract data or subelement from element.

        :param element: The target data node element.
        :type element: Any

        :returns: Data or subelement.
        :rtype: Any

        :raises ~data_extractor.exceptions.ExprError: Extractor Expression Error.
        """
        raise NotImplementedError

    def extract_first(self, element: Any, default: Any = sentinel) -> Any:
        """
        Extract the first data or subelement from `extract` method call result.

        :param element: The target data node element.
        :type element: Any
        :param default: Default value when not found. \
            Default: :data:`data_extractor.utils.sentinel`.
        :type default: Any, optional

        :returns: Data or subelement.
        :rtype: Any

        :raises ~data_extractor.exceptions.ExtractError: \
            Thrown by extractor extracting wrong data.
        """
        rv = self.extract(element)
        if not rv:
            if default is sentinel:
                # Local Folder
                from .exceptions import ExtractError

                raise ExtractError(self, element)

            return default

        return rv[0]


class AbstractComplexExtractor(metaclass=ComplexExtractorMeta):
    """
    Abstract Complex Extractor Clase.

    Its metaclass is :class:`data_extractor.core.ComplexExtractorMeta`
    """

    @abstractmethod
    def extract(self, element: Any) -> Any:
        """
        Extract the wanted data.

        :param element: The target data node element.
        :type element: Any

        :returns: Data or subelement.
        :rtype: Any

        :raises ~data_extractor.exceptions.ExtractError: \
            Thrown by extractor extracting wrong data.
        """
        raise NotImplementedError


AbstractExtractors = Union[AbstractSimpleExtractor, AbstractComplexExtractor]

__all__ = (
    "AbstractComplexExtractor",
    "AbstractExtractors",
    "AbstractSimpleExtractor",
    "ComplexExtractorMeta",
    "SimpleExtractorMeta",
)
