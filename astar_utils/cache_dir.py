# -*- coding: utf-8 -*-
"""Common cache location for Astar packages with support for ScopeSim_Data.

This was previously only used in skycalc_ipy, and some other packages had the
home/.astar/ location hardcoded. Moving it here allows to define this in one
place in case we need to change it at some point.

`ScopeSim_Data` is imported dynamically when `get_cache_dir()` is called. This
removes the need to add it as a dependency, preventing any circular issues.

```mmd
flowchart TD
    read --> A{ScopeSim_Data<br>installed?}
    A --True--> C(look in ScopeSim_Data)
    A --False--> D(look in ~/.astar)
    C --not found--> D
    write --> B{CI flag?}
    B --True--> E(save to ScopeSim_Data)
    B --False--> F(save to ~/.astar)
```

"""

from pathlib import Path
from importlib import import_module


def get_read_cache_dir(package_name: str | None = None) -> Path:
    """
    Establish the cache directories used for reading.

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
    cache_dirs = []

    try:
        sim_data = import_module("scopesim_data")
        if package_name is not None:
            cache_dirs.append(getattr(sim_data, f"dir_cache_{package_name}"))
        else:
            cache_dirs.append(sim_data.dir_cache)
    except (ImportError, AttributeError):
        dir_cache_root = Path.home() / ".astar"
        if package_name is not None:
            cache_dirs.append(dir_cache_root / package_name)
        else:
            cache_dirs.append(dir_cache_root)

    for cache_dir in cache_dirs:
        if not cache_dir.is_dir():
            cache_dir.mkdir(parents=True)

    return cache_dirs


def get_write_cache_dir(package_name: str | None = None) -> Path:
    """
    Establish the cache directories used for writing.

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
    cache_dir : Path
        Cache directory as pathlib Path.
    """
    try:
        sim_data = import_module("scopesim_data")
        if package_name is not None:
            cache_dir = getattr(sim_data, f"dir_cache_{package_name}")
        else:
            cache_dir = sim_data.cache_dir
    except (ImportError, AttributeError):
        cache_dir = Path.home() / ".astar"
        if package_name is not None:
            cache_dir = cache_dir / package_name

    if not cache_dir.is_dir():
        cache_dir.mkdir(parents=True)

    return cache_dir
