# thorcam

![Versions](https://img.shields.io/badge/python->3.9-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/sdss-thorcam/badge/?version=latest)](https://sdss-thorcam.readthedocs.io/en/latest/?badge=latest)
[![Tests Status](https://github.com/sdss/thorcam/workflows/Test/badge.svg)](https://github.com/sdss/thorcam/actions)
[![Build Status](https://github.com/sdss/thorcam/workflows/Build/badge.svg)](https://github.com/sdss/thorcam/actions)
[![codecov](https://codecov.io/gh/sdss/thorcam/branch/master/graph/badge.svg)](https://codecov.io/gh/sdss/thorcam)

A library to control Thorlabs Zelux CMOS cameras.

## Installation

In general you should be able to install ``thorcam`` by doing

```console
pip install sdss-thorcam
```

To build from source, use

```console
git clone git@github.com:sdss/thorcam
cd thorcam
pip install .[docs]
```

## Development

`thorcam` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. To work with an editable install it's recommended that you setup `poetry` and install `thorcam` in a virtual environment by doing

```console
poetry install
```

pip does not support editable installs with PEP-517 yet. That means that running `pip install -e .` will fail because `poetry` doesn't use a `setup.py` file. As a workaround, you can use the `create_setup.py` file to generate a temporary `setup.py` file. To install `thorcam` in editable mode without `poetry`, do

```console
pip install poetry
python create_setup.py
pip install -e .
```
