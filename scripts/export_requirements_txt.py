# Standard Library
import shlex
import subprocess

from pathlib import Path


def fix_end_of_file(text):
    return text.rstrip() + "\n"


def pdm_export(sections, filename, dev=False):
    if sections:
        args = " -s ".join([""] + sections)
    else:
        args = ""

    if dev:
        args = " -d" + args

    output = subprocess.check_output(
        shlex.split(f"pdm export -f requirements {args}"), encoding="utf-8"
    )
    output = fix_end_of_file(output)

    p = Path(filename)
    if p.read_text() != output:
        p.write_text(output)


pdm_export(sections=[], filename="requirements-mini.txt")
pdm_export(
    sections=[
        "lxml",
        "cssselect",
        "jsonpath-extractor",
        "jsonpath-rw",
        "jsonpath-rw-ext",
    ],
    filename="requirements.txt",
)
pdm_export(
    sections=["docs", "build_readme", "test"], filename="requirements-dev.txt", dev=True
)
