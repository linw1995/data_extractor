============
Contributing
============


Environment Setup
~~~~~~~~~~~~~~~~~

Clone the source codes from Github.

.. code-block:: shell

    git clone https://github.com/linw1995/data_extractor.git
    cd data_extractor

Setup the development environment.
Please make sure you install the pdm_ CLI in your environment.

.. code-block:: shell

    make init
    make PYTHON=3.7 init  # for specific python version

.. _pdm: https://github.com/pdm-project/pdm

Linting
~~~~~~~

Use pre-commit_ for installing linters to ensure a good code style.

.. code-block:: shell

    make pre-commit

Run linters.

.. code-block:: shell

    make check-all

.. _pre-commit: https://pre-commit.com/

Testing
~~~~~~~

Run quick tests.

.. code-block:: shell

    make

Run quick tests with verbose.

.. code-block:: shell

    make vtest

Run tests with coverage.

.. code-block:: shell

    make cov
