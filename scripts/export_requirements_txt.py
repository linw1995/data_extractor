# Standard Library
import shlex
import subprocess

from pathlib import Path


def fix_end_of_file(text):
    return text.rstrip() + "\n"


def pdm_export(args, filename):

    output = subprocess.check_output(
        shlex.split(f"pdm export -f requirements {' '.join(args)}"), encoding="utf-8"
    )
    output = fix_end_of_file(output)

    p = Path(filename)
    is_new = not p.exists()
    if is_new or p.read_text() != output:
        p.write_text(output)

    if is_new:
        raise RuntimeError("Create a new file")


pdm_export(args=[], filename="requirements-mini.txt")
pdm_export(
    args=[
        "-s:all",
    ],
    filename="requirements.txt",
)
pdm_export(args=["-d", "-ds:all"], filename="requirements-dev.txt")
pdm_export(args=["-ds", "docs"], filename="requirements-docs.txt")
