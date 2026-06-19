# -*- coding: utf-8 -*-
"""Common cache location for Astar packages with support for ScopeSim_Data.

Previously each package handled this on its own (skycalc_ipy had a working
version, others hardcoded ``~/.astar/``). Centralising it here means the logic
lives in one place at the bottom of the dependency tree.

``scopesim_data`` is imported lazily inside the functions, so it never needs to
be a hard dependency of ``astar-utils`` (which would create a circular tie).

Reading and writing follow different rules. Reading searches several locations
in priority order and returns the first hit. Writing goes to the user's home
cache *unless* the ``SCOPESIM_DATA_CI_FLAG`` environment flag is set -- this
flag is meant to be set **only** in ScopeSim_Data's own CI, when the committed
data bundle is being refreshed. A regular user who merely has ``scopesim_data``
installed therefore reads from it but never writes into it (which would land in
a read-only ``site-packages`` and never be committed anyway).

```mermaid
flowchart TD
    subgraph reading [find_cached_file / iter_read_cache_dirs]
        direction TB
        R0([need a file]) --> R1{scopesim_data<br>installed?}
        R1 -- yes --> R2[look in<br>scopesim_data/PKG]
        R1 -- no --> R3[look in caller's<br>bundled data dirs]
        R2 -- found --> RF([return path])
        R2 -- not found --> R3
        R3 -- found --> RF
        R3 -- not found --> R4[look in<br>~/.astar/PKG]
        R4 -- found --> RF
        R4 -- not found --> RN([return None -> download])
    end
    subgraph writing [get_write_cache_dir]
        direction TB
        W0([store a download]) --> W1{CI flag set?}
        W1 -- yes --> W2[write into<br>scopesim_data/PKG]
        W1 -- no --> W3[write into<br>~/.astar/PKG]
    end
```

"""

from os import environ
from pathlib import Path
from importlib import import_module
from collections.abc import Iterator, Iterable

__all__ = [
    "iter_read_cache_dirs",
    "find_cached_file",
    "get_write_cache_dir",
    "SIM_DATA_CI_ENV",
    "HOME_CACHE",
]

# Environment variable that, when set to a non-empty value, redirects writes
# into the installed ``scopesim_data`` tree. Intended to be set **only** in
# ScopeSim_Data's own CI run.
SIM_DATA_CI_ENV: str = "SCOPESIM_DATA_CI_FLAG"

# Fallback cache root in the user's home directory.
HOME_CACHE: Path = Path.home() / ".astar"


def _scopesim_data_root() -> Path | None:
    """Return the ``scopesim_data`` cache root, or None if not installed."""
    try:
        sim_data = import_module("scopesim_data")
    except ImportError:
        return None
    return Path(sim_data.cache_dir)


def _pkg_subdir(root: Path, package_name: str | None) -> Path:
    """Append `package_name` as a subfolder to `root`, if given."""
    if package_name is None:
        return root
    return root / package_name


def iter_read_cache_dirs(
    package_name: str | None = None,
    extra_dirs: Iterable[Path] = (),
    *,
    include_home_cache: bool = True,
) -> Iterator[Path]:
    """Yield cache directories to read from, in priority order.

    The directories are, in order:

    1. The ``scopesim_data`` cache (only if that package is installed).
    2. Any `extra_dirs` supplied by the caller, e.g. a package's own bundled
       data directory (present in a source clone, possibly absent on PyPI).
    3. The ``.astar`` cache in the user's home directory, where previously
       downloaded files are stored (unless ``include_home_cache`` is False).

    Directories are yielded whether or not they exist; callers check for the
    actual file (see ``find_cached_file``). Nothing is created here.

    Parameters
    ----------
    package_name : str or None, optional
        Name of the Astar package. If given, appended as a subfolder to the
        ScopeSim_Data and home cache roots. If None, the roots are yielded.
    extra_dirs : iterable of Path, optional
        Extra directories, inserted after ScopeSim_Data but before the home
        cache. Used for package-bundled data.
    include_home_cache : bool, optional
        Whether to yield the home cache as the last location (default True).
        Set this to False when the home cache is managed by something else
        that should own it -- e.g. a `pooch.Pooch` whose ``path`` is the home
        cache and which does its own hash check there. In that case this
        function only yields the "trusted local" locations to pre-check before
        delegating to that handler.

    Yields
    ------
    Path
        Candidate cache directory.
    """
    if (root := _scopesim_data_root()) is not None:
        yield _pkg_subdir(root, package_name)
    for extra in extra_dirs:
        yield Path(extra)
    if include_home_cache:
        yield _pkg_subdir(HOME_CACHE, package_name)


def find_cached_file(
    relpath: Path,
    package_name: str | None = None,
    extra_dirs: Iterable[Path] = (),
    *,
    include_home_cache: bool = True,
) -> Path | None:
    """Return the first existing ``cache_dir / relpath``, or None.

    Searches the directories from ``iter_read_cache_dirs`` in priority order.
    A return value of None signals that the caller should download the file
    and store it via ``get_write_cache_dir``.

    Parameters
    ----------
    relpath : Path
        Path of the file relative to a cache directory.
    package_name, extra_dirs
        Passed through to ``iter_read_cache_dirs``.

    Returns
    -------
    Path or None
        Full path to the located file, or None if not found anywhere.
    """
    relpath = Path(relpath)
    for cache_dir in iter_read_cache_dirs(
            package_name, extra_dirs, include_home_cache=include_home_cache):
        if (candidate := cache_dir / relpath).is_file():
            return candidate
    return None


def get_write_cache_dir(package_name: str | None = None) -> Path:
    """Return the directory to write downloaded files into.

    This is the ``.astar`` cache in the user's home directory, unless the
    ``SIM_DATA_CI_ENV`` environment variable is set to a non-empty value, in
    which case writes are redirected into the installed ``scopesim_data`` tree.
    That flag should only ever be set in ScopeSim_Data's own CI run.

    The returned directory is created (including parents) if necessary.

    Parameters
    ----------
    package_name : str or None, optional
        Name of the Astar package, appended as a subfolder if given.

    Returns
    -------
    Path
        Writable cache directory.

    Raises
    ------
    RuntimeError
        If `SIM_DATA_CI_ENV` is set but ``scopesim_data`` is not installed.
    """
    if environ.get(SIM_DATA_CI_ENV):
        if (root := _scopesim_data_root()) is None:
            raise RuntimeError(
                f"{SIM_DATA_CI_ENV} is set, but scopesim_data is not "
                "installed; cannot write into the data bundle."
            )
    else:
        root = HOME_CACHE

    cache_dir = _pkg_subdir(root, package_name)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
