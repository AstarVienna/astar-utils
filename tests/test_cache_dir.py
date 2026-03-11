# -*- coding: utf-8 -*-
"""Unit tests for cache_dir."""

from astar_utils.cache_dir import get_cache_dir


def test_cache_dir_root():
    cache_dir = get_cache_dir()
    # Could be either, depending on whether ScopeSim_Data is installed.
    assert any(loc in cache_dir.parts for loc in {"scopesim_data", ".astar"})


def test_cache_dir_pkg():
    cache_dir = get_cache_dir("bogus")
    # Should always be in .astar, because "bogus" is not in ScopeSim_Data.
    assert cache_dir.parts[-2:] == (".astar", "bogus")
