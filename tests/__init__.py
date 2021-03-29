# Standard Library
import platform
import sys

from pathlib import Path

current_python_version = "%s.%s" % platform.python_version_tuple()[:2]

# when executing pytest cli, the sys.path will be changed.
# jsonpath-extractor package's module `jsonpath` same as
# the file `jsonpath.py` in f'{sys.prefix}/bin'.
# So need to remove it to avoid import the wrong module.
for p in [
    Path(f"{sys.prefix}/bin/jsonpath.py"),
    Path(f"__pypackages__/{current_python_version}/bin/jsonpath.py"),
]:
    if p.exists():
        p.unlink()

# pdm
