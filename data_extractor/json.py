"""
===================================================
:mod:`json` -- Extractors for JSON data extracting.
===================================================
"""
# Standard Library
from typing import Any, Dict, Optional, Tuple, Type

# Local Folder
from .abc import AbstractSimpleExtractor
from .exceptions import ExprError
from .utils import create_dummy_extractor_cls, is_dummy_extractor_cls


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
        cls: Type["JSONExtractor"], *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> "JSONExtractor":
        if json_extractor_backend is None:
            raise RuntimeError(
                "'jsonpath-extractor', 'jsonpath-rw' or 'jsonpath-rw-ext' "
                "package is needed, run pip to install it. "
            )

        if json_extractor_backend in cls.__mro__:
            # __new__ called by deep copy
            return super(JSONExtractor, cls).__new__(cls)

        # rename into JSONExtractor
        obj = super(JSONExtractor, cls).__new__(
            type("JSONExtractor", (json_extractor_backend,), {})
        )
        obj.__init__(*args, **kwargs)
        return obj


JSONPathRWExtractor = None

try:
    # Third Party Library
    import jsonpath_rw

    from jsonpath_rw import JSONPath
    from jsonpath_rw.lexer import JsonPathLexerError

    class JSONPathRWExtractor(JSONExtractor):
        """
        Use JSONPath expression implementated by **jsonpath-rw** package
        for JSON data extracting.

        Before extracting, should parse the JSON text into Python object.

        :param expr: JSONPath Expression.
        :type expr: str
        """

        def __init__(self, expr: str) -> None:
            super().__init__(expr)
            self._jsonpath: Optional[JSONPath] = None

        def build(self) -> None:
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

    # Third Party Library
    import jsonpath_rw_ext

    class JSONPathRWExtExtractor(JSONPathRWExtractor):
        """
        Use JSONPath expression implementated by **jsonpath-rw-ext** package
        for JSON data extracting.

        Before extracting, should parse the JSON text into Python object.

        :param expr: JSONPath Expression.
        :type expr: str
        """

        def build(self) -> None:
            try:
                self._jsonpath = jsonpath_rw_ext.parse(self.expr)
                self.built = True
            except (JsonPathLexerError, Exception) as exc:
                # jsonpath_rw.parser.JsonPathParser.p_error raises exc of Exception type
                raise ExprError(extractor=self, exc=exc) from exc


except ImportError:
    if JSONPathRWExtractor is None:
        JSONPathRWExtractor = create_dummy_extractor_cls(
            "JSONPathRWExtractor", "jsonpath-rw"
        )

    JSONPathRWExtExtractor = create_dummy_extractor_cls(
        "JSONPathRWExtExtractor", "jsonpath-rw-ext"
    )

try:
    # Third Party Library
    import jsonpath

    from jsonpath import Expr

    class JSONPathExtractor(JSONExtractor):
        """
        Use JSONPath expression implementated by **jsonpath-extractor** package
        for JSON data extracting.

        Before extracting, should parse the JSON text into Python object.

        :param expr: JSONPath Expression.
        :type expr: str
        """

        def __init__(self, expr: str) -> None:
            super().__init__(expr)
            self._jsonpath: Optional[Expr] = None

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


except ImportError:
    JSONPathExtractor = create_dummy_extractor_cls(
        "JSONPathExtractor", "jsonpath-extractor"
    )


json_extractor_backend: Optional[Type[JSONExtractor]] = None
if not is_dummy_extractor_cls(JSONPathExtractor):
    json_extractor_backend = JSONPathExtractor
elif not is_dummy_extractor_cls(JSONPathRWExtExtractor):
    json_extractor_backend = JSONPathRWExtExtractor
elif not is_dummy_extractor_cls(JSONPathRWExtractor):
    json_extractor_backend = JSONPathRWExtractor


__all__ = (
    "JSONExtractor",
    "JSONPathExtractor",
    "JSONPathRWExtExtractor",
    "JSONPathRWExtractor",
    "json_extractor_backend",
)
