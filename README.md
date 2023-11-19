# Astar Utils

[![Tests](https://github.com/AstarVienna/astar-utils/actions/workflows/tests.yml/badge.svg)](https://github.com/AstarVienna/astar-utils/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/AstarVienna/astar-utils/graph/badge.svg)](https://codecov.io/gh/AstarVienna/astar-utils)
![PyPI - Version](https://img.shields.io/pypi/v/astar-utils)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/astar-utils)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This package is devloped and maintained by [Astar Vienna](https://github.com/AstarVienna) and contains commonly-used utilities for the group's projects to avoid both duplicating code and circular dependencies.

## Contents

The package currently contains the following public functions and classes:

- `NestedMapping`: a `dict`-like structure supporting !-style nested keys.
- `UniqueList`: a `list`-like structure with no duplicate elements and some convenient methods.

## Dependencies

Dependencies are intentionally kept to a minimum for simplicity. Current dependencies are:

- `more-itertools`
- `pyyaml`

Version requirement for these dependencies can be found in the `pyproject.toml` file.
