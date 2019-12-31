# Standard Library
from pathlib import Path


# when executing pytest cli, the sys.path will be changed.
# jsonpath-extractor package's module `jsonpath` same as
# the file `jsonpath.py` in f'{sys.prefix}/bin'.
# So need to remove it to avoid import the wrong module.
jsonpath_file = Path(".venv/bin/jsonpath.py")
if jsonpath_file.exists():
    jsonpath_file.unlink()
