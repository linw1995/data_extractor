# encoding: utf-8
import pathlib
import re

from setuptools import setup


here = pathlib.Path(__file__).parent

txt = (here / "data_extractor" / "__init__.py").read_text("utf-8")
try:
    version = re.findall(r"""^__version__ = "([^']+)"\r?$""", txt, re.M)[0]
except IndexError:
    raise RuntimeError("Unable to determine version.")

long_description = "\n\n".join(
    [(here / "README.md").read_text("utf-8"), (here / "CHANGES.md").read_text("utf-8")]
)

install_requires = ["cssselect>=1.0.3", "jsonpath-rw>=1.4.0", "lxml>=4.3.0"]


tests_require = ["pytest>=3.6"]


setup(
    name="data_extractor",
    version=version,
    description="Combine XPath, CSS Selector and JSONPath for Web data extracting.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    author="林玮",
    author_email="linw1995@icloud.com",
    url="https://github.com/linw1995/data_extractor",
    project_urls={
        "GitHub: issues": "https://github.com/linw1995/data_extractor/issues",
        "GitHub: repo": "https://github.com/linw1995/data_extractor",
        "GitHub Pages: docs": "https://linw1995.com/data_extractor",
    },
    license="MIT",
    packages=["data_extractor"],
    python_requires=">=3.7",
    install_requires=install_requires,
    tests_require=tests_require,
)
