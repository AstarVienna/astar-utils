# -*- coding: utf-8 -*-
"""Common cache location for Astar packages with support for ScopeSim_Data.

This was previously only used in skycalc_ipy, and some other packages had the
home/.astar/ location hardcoded. Moving it here allows to define this in one
place in case we need to change it at some point.

`ScopeSim_Data` is imported dynamically when `get_cache_dir()` is called. This
removes the need to add it as a dependency, preventing any circular issues.
"""

from pathlib import Path
from importlib import import_module


def get_cache_dir(package_name: str | None = None) -> Path:
    """
    Establish the cache directory.

    First checks if ScopeSim_Data is installed and if the given package (if any)
    has a cache dir defined there. Otherwise, default to ".astar/" in the user's
    home directory.

    If the resulting directory doesn't exist yet, it is created including all
    required parent directories.

    Parameters
    ----------
    package_name : str | None, optional
        Name of Astar package to look for in ScopeSim_Data. If None (default),
        the parent cache directory is returned.

    Returns
    -------
    dir_cache : Path
        Cache directory as pathlib Path.

    """
    try:
        sim_data = import_module("scopesim_data")
        if package_name is not None:
            dir_cache = getattr(sim_data, f"dir_cache_{package_name}")
        else:
            dir_cache = sim_data.dir_cache
    except (ImportError, AttributeError):
        dir_cache = Path.home() / ".astar"
        if package_name is not None:
            dir_cache = dir_cache / package_name

    if not dir_cache.is_dir():
        dir_cache.mkdir(parents=True)

    return dir_cache
