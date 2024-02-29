"""
===================================================
:mod:`json` -- Extractors for JSON data extracting.
===================================================
"""

# Standard Library
from typing import TYPE_CHECKING, Any, Optional, Type

# Local Folder
from .core import AbstractSimpleExtractor
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

    def __new__(
        cls: Type["JSONExtractor"], *args: Any, **kwargs: Any
    ) -> "JSONExtractor":
        if json_extractor_backend is None:
            raise RuntimeError(
                "'jsonpath-extractor', 'jsonpath-rw' or 'jsonpath-rw-ext' "
                "package is needed, run pip to install it. "
            )

        obj: JSONExtractor
        if cls is JSONExtractor:
            # invoke the json extractor backend for object creation
            # TODO: cache renamed type
            obj = super(AbstractSimpleExtractor, cls).__new__(
                type(
                    "JSONExtractor", (json_extractor_backend,), {}
                )  # rename into JSONExtractor
            )
        else:
            # invoke subclasses directly
            obj = super(AbstractSimpleExtractor, cls).__new__(cls)

        return obj

    def extract(self, element: Any) -> Any:
        raise NotImplementedError


try:
    # Third Party Library
    import jsonpath_rw

    _missing_jsonpath_rw = False
except ImportError:
    _missing_jsonpath_rw = True


class JSONPathRWExtractor(JSONExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-rw** package
    for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    if TYPE_CHECKING:
        # Third Party Library
        from jsonpath_rw import JSONPath
    _jsonpath = Property["JSONPath"]()

    def __init__(self, expr: str) -> None:
        super(JSONExtractor, self).__init__(expr)
        if _missing_jsonpath_rw:
            _missing_dependency("jsonpath-rw")

        # Third Party Library
        from jsonpath_rw.lexer import JsonPathLexerError

        try:
            self._jsonpath = jsonpath_rw.parse(self.expr)
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
        return [m.value for m in self._jsonpath.find(element)]


try:
    # Third Party Library
    import jsonpath_rw_ext

    _missing_jsonpath_rw_ext = False
except ImportError:
    _missing_jsonpath_rw_ext = True


class JSONPathRWExtExtractor(JSONPathRWExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-rw-ext** package
    for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    if TYPE_CHECKING:
        # Third Party Library
        from jsonpath_rw_ext import JSONPath as JSONPathExt
    _jsonpath = Property["JSONPathExt"]()

    def __init__(self, expr: str) -> None:
        super(JSONExtractor, self).__init__(expr)
        if _missing_jsonpath_rw_ext:
            _missing_dependency("jsonpath-rw-ext")

        # Third Party Library
        from jsonpath_rw.lexer import JsonPathLexerError

        try:
            self._jsonpath = jsonpath_rw_ext.parse(self.expr)
        except (JsonPathLexerError, Exception) as exc:
            # jsonpath_rw.parser.JsonPathParser.p_error raises exc of Exception type
            raise ExprError(extractor=self, exc=exc) from exc


try:
    # Third Party Library
    import jsonpath

    _missing_jsonpath = False
except ImportError:
    _missing_jsonpath = True


class JSONPathExtractor(JSONExtractor):
    """
    Use JSONPath expression implementated by **jsonpath-extractor** package
    for JSON data extracting.

    Before extracting, should parse the JSON text into Python object.

    :param expr: JSONPath Expression.
    :type expr: str
    """

    if TYPE_CHECKING:
        # Third Party Library
        from jsonpath import Expr

    _jsonpath = Property["Expr"]()

    def __init__(self, expr: str) -> None:
        super(JSONExtractor, self).__init__(expr)

        if _missing_jsonpath:
            _missing_dependency("jsonpath-extractor")

        try:
            self._jsonpath = jsonpath.parse(self.expr)
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
