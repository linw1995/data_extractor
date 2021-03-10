# Standard Library
import warnings

# Local Folder
from . import core

warnings.warn(
    f"module {__name__} is deprecated, use {core.__name__} instead", stacklevel=2
)

# Local Folder
from .core import *  # noqa: F4, E4
