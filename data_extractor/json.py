"""
===================================================
:mod:`json` -- Extractors for JSON data extracting.
===================================================
"""
# Standard Library
from typing import TYPE_CHECKING, Any, Optional, Type

# Local Folder
from .abc import AbstractSimpleExtractor, SimpleExtractorMeta
from .exceptions import ExprError
from .utils import Property, _missing_dependency


class JSONExtractor(AbstractSimpleExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-extractor**,
    **jsonpath-rw** or **jsonpath-rw-ext** packages for JSON data extracting.
    Change **json_extractor_backend** value to indicate which package to use.

    >>> import data_extractor.json
    >>> from data_extractor.json import JSONPathExtractor
    >>> data_extractor.json.json_extractor_backend = JSONPathExtractor

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    def __new__(cls: SimpleExtractorMeta, *args: Any, **kwargs: Any) -> "JSONExtractor":
        if json_extractor_backend is None:
            raise RuntimeError(
                "'jsonpath-extractor', 'jsonpath-rw' or 'jsonpath-rw-ext' "
                "package is needed, run pip to install it. "
            )

        if json_extractor_backend in cls.__mro__:
            # __new__ called by deep copy
            return super(JSONExtractor, cls).__new__(cls)

        if cls is JSONExtractor:
            obj = super(JSONExtractor, cls).__new__(
                type(
                    "JSONExtractor", (json_extractor_backend,), {}
                )  # rename into JSONExtractor
            )
        else:
            obj = super(JSONExtractor, cls).__new__(cls)

        obj.__init__(*args, **kwargs)
        return obj

    def build(self):
        raise NotImplementedError

    def extract(self, element):
        raise NotImplementedError


try:
    # Third Party Library
    import jsonpath_rw

    _missing_jsonpath_rw = False
except ImportError:
    _missing_jsonpath_rw = True

if TYPE_CHECKING:
    # Third Party Library
    from jsonpath_rw import JSONPath


class JSONPathRWExtractor(JSONExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-rw** package
    for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    _jsonpath = Property[Optional["JSONPath"]]()  # TODO: CacheProperty

    def __init__(self, expr: str) -> None:
        super().__init__(expr)
        if _missing_jsonpath_rw:
            _missing_dependency("jsonpath-rw")

        self._jsonpath = None

    def build(self) -> None:
        # Third Party Library
        from jsonpath_rw.lexer import JsonPathLexerError

        try:
            self._jsonpath = jsonpath_rw.parse(self.expr)
            self.built = True
        except (JsonPathLexerError, Exception) as exc:
            # jsonpath_rw.parser.JsonPathParser.p_error raises exc of Exception type
            raise ExprError(extractor=self, exc=exc) from exc

    def extract(self, element: Any) -> Any:
        """
        Extract data from JSON data.

        :param element: Python object parsed from JSON text.
        :type element: Any

        :returns: Data.
        :rtype: Any
        """
        if not self.built:
            self.build()

        assert self._jsonpath is not None
        return [m.value for m in self._jsonpath.find(element)]


try:
    # Third Party Library
    import jsonpath_rw_ext

    _missing_jsonpath_rw_ext = False
except ImportError:
    _missing_jsonpath_rw_ext = True

if TYPE_CHECKING:
    # Third Party Library
    from jsonpath_rw_ext import JSONPath as JSONPathExt


class JSONPathRWExtExtractor(JSONPathRWExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-rw-ext** package
    for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    _jsonpath = Property[Optional["JSONPathExt"]]()  # TODO: CacheProperty

    def __init__(self, expr: str) -> None:
        super().__init__(expr)
        if _missing_jsonpath_rw_ext:
            _missing_dependency("jsonpath-rw-ext")

    def build(self) -> None:
        # Third Party Library
        from jsonpath_rw.lexer import JsonPathLexerError

        try:
            self._jsonpath = jsonpath_rw_ext.parse(self.expr)
            self.built = True
        except (JsonPathLexerError, Exception) as exc:
            # jsonpath_rw.parser.JsonPathParser.p_error raises exc of Exception type
            raise ExprError(extractor=self, exc=exc) from exc


try:
    # Third Party Library
    import jsonpath

    _missing_jsonpath = False
except ImportError:
    _missing_jsonpath = True


if TYPE_CHECKING:
    # Third Party Library
    from jsonpath import Expr


class JSONPathExtractor(JSONExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-extractor** package
    for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    _jsonpath = Property[Optional["Expr"]]()  # TODO: CacheProperty

    def __init__(self, expr: str) -> None:
        super().__init__(expr)

        if _missing_jsonpath:
            _missing_dependency("jsonpath-extractor")

        self._jsonpath = None

    def build(self) -> None:
        try:
            self._jsonpath = jsonpath.parse(self.expr)
            self.built = True
        except SyntaxError as exc:
            raise ExprError(extractor=self, exc=exc) from exc

    def extract(self, element: Any) -> Any:
        """
        Extract data from JSON data.

        :param element: Python object parsed from JSON text.
        :type element: Any

        :returns: Data.
        :rtype: Any
        """
        if not self.built:
            self.build()

        assert self._jsonpath is not None
        return self._jsonpath.find(element)


json_extractor_backend: Optional[Type[JSONExtractor]] = None
if not _missing_jsonpath:
    json_extractor_backend = JSONPathExtractor
elif not _missing_jsonpath_rw_ext:
    json_extractor_backend = JSONPathRWExtExtractor
elif not _missing_jsonpath_rw:
    json_extractor_backend = JSONPathRWExtractor


__all__ = (
    "JSONExtractor",
    "JSONPathExtractor",
    "JSONPathRWExtExtractor",
    "JSONPathRWExtractor",
    "json_extractor_backend",
)
