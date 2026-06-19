# -*- coding: utf-8 -*-
"""Unit tests for cache_dir."""

from pathlib import Path

import pytest

from astar_utils import cache_dir as cd


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Redirect the home cache to a temporary directory."""
    home_cache = tmp_path / "home" / ".astar"
    monkeypatch.setattr(cd, "HOME_CACHE", home_cache)
    return home_cache


@pytest.fixture
def no_scopesim_data(monkeypatch):
    """Pretend scopesim_data is not installed."""
    monkeypatch.setattr(cd, "_scopesim_data_root", lambda: None)


@pytest.fixture
def fake_scopesim_data(tmp_path, monkeypatch):
    """Pretend scopesim_data is installed, with its cache in tmp_path."""
    root = tmp_path / "scopesim_data" / "data"
    monkeypatch.setattr(cd, "_scopesim_data_root", lambda: root)
    return root


@pytest.fixture(autouse=True)
def clear_sim_data_flag(monkeypatch):
    """Ensure the sim data CI flag never leaks in from the environment."""
    monkeypatch.delenv(cd.SIM_DATA_CI_ENV, raising=False)


class TestIterReadCacheDirs:
    def test_order_without_scopesim_data(self, no_scopesim_data, fake_home):
        dirs = list(cd.iter_read_cache_dirs("spextra", [Path("/bundled")]))
        assert dirs == [Path("/bundled"), fake_home / "spextra"]

    def test_order_with_scopesim_data(self, fake_scopesim_data, fake_home):
        dirs = list(cd.iter_read_cache_dirs("spextra", [Path("/bundled")]))
        assert dirs == [
            fake_scopesim_data / "spextra",
            Path("/bundled"),
            fake_home / "spextra",
        ]

    def test_no_package_name_yields_roots(self, fake_scopesim_data, fake_home):
        dirs = list(cd.iter_read_cache_dirs())
        assert dirs == [fake_scopesim_data, fake_home]

    def test_does_not_create_dirs(self, no_scopesim_data, fake_home):
        list(cd.iter_read_cache_dirs("spextra"))
        assert not fake_home.exists()


class TestFindCachedFile:
    def test_bundled_beats_home_cache(
        self, no_scopesim_data, fake_home, tmp_path
    ):
        bundled = tmp_path / "bundled"
        for base in (bundled, fake_home / "spextra"):
            (base / "svo").mkdir(parents=True)
            (base / "svo" / "filt").write_text("x")
        found = cd.find_cached_file(Path("svo/filt"), "spextra", [bundled])
        assert found == bundled / "svo" / "filt"

    def test_scopesim_data_beats_everything(
        self, fake_scopesim_data, fake_home, tmp_path
    ):
        bundled = tmp_path / "bundled"
        for base in (fake_scopesim_data / "spextra", bundled):
            (base / "svo").mkdir(parents=True)
            (base / "svo" / "filt").write_text("x")
        found = cd.find_cached_file(Path("svo/filt"), "spextra", [bundled])
        assert found == fake_scopesim_data / "spextra" / "svo" / "filt"

    def test_falls_through_to_home(
        self, no_scopesim_data, fake_home, tmp_path
    ):
        (fake_home / "spextra" / "svo").mkdir(parents=True)
        (fake_home / "spextra" / "svo" / "filt").write_text("x")
        found = cd.find_cached_file(
            Path("svo/filt"), "spextra", [tmp_path / "empty"]
        )
        assert found == fake_home / "spextra" / "svo" / "filt"

    def test_returns_none_when_missing(self, no_scopesim_data, fake_home):
        assert cd.find_cached_file(Path("nope"), "spextra") is None


class TestGetWriteCacheDir:
    def test_defaults_to_home(self, no_scopesim_data, fake_home):
        target = cd.get_write_cache_dir("spextra")
        assert target == fake_home / "spextra"
        assert target.is_dir()

    def test_home_even_when_scopesim_data_installed(
        self, fake_scopesim_data, fake_home
    ):
        target = cd.get_write_cache_dir("spextra")
        assert target == fake_home / "spextra"

    def test_sim_data_flag_writes_to_scopesim_data(
        self, fake_scopesim_data, monkeypatch
    ):
        monkeypatch.setenv(cd.SIM_DATA_CI_ENV, "1")
        target = cd.get_write_cache_dir("spextra")
        assert target == fake_scopesim_data / "spextra"
        assert target.is_dir()

    def test_sim_data_flag_without_scopesim_data_raises(
        self, no_scopesim_data, monkeypatch
    ):
        monkeypatch.setenv(cd.SIM_DATA_CI_ENV, "1")
        with pytest.raises(RuntimeError):
            cd.get_write_cache_dir("spextra")

    def test_no_package_name_returns_root(self, no_scopesim_data, fake_home):
        assert cd.get_write_cache_dir() == fake_home


class TestIncludeHomeCache:
    def test_excludes_home_cache(self, fake_scopesim_data, fake_home):
        dirs = list(
            cd.iter_read_cache_dirs(
                "spextra", [Path("/bundled")], include_home_cache=False
            )
        )
        assert dirs == [fake_scopesim_data / "spextra", Path("/bundled")]
        assert fake_home / "spextra" not in dirs

    def test_find_skips_home_cache_when_excluded(
        self, no_scopesim_data, fake_home
    ):
        # File only in the home cache -> not found when home cache excluded.
        (fake_home / "spextra").mkdir(parents=True)
        (fake_home / "spextra" / "x").write_text("x")
        assert (
            cd.find_cached_file(Path("x"), "spextra", include_home_cache=False)
            is None
        )
        # ...but found with the default behaviour.
        assert (
            cd.find_cached_file(Path("x"), "spextra")
            == fake_home / "spextra" / "x"
        )
