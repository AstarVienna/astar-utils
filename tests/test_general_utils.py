# -*- coding: utf-8 -*-
"""Unit tests for general_utils.py."""

import pytest

from astar_utils import close_loop, stringify_dict, check_keys, AstarWarning


def test_close_loop():
    initer = [1, 2, 3]
    outiter = close_loop(initer)
    assert list(outiter) == initer + [1]


def test_stringify_dict():
    indic = {"a": "foo", "b": 42, "c": [1, 2, 3], "d": True}
    outdic = dict(stringify_dict(indic))
    assert outdic["a"] == indic["a"]
    assert outdic["b"] == indic["b"]
    assert outdic["c"] == str(indic["c"])
    assert outdic["d"] == indic["d"]


class TestCheckKeys:
    @pytest.mark.filterwarnings("ignore::UserWarning")
    @pytest.mark.parametrize(("req", "res"), [({"foo", "baz"}, True),
                                              ({"bogus", "baz"}, False)])
    def test_warn_all(self, req, res):
        tstdic = {"foo": 5, "bar": 2, "baz": 7}
        assert check_keys(tstdic, req, action="warning") is res

    @pytest.mark.filterwarnings("ignore::UserWarning")
    @pytest.mark.parametrize(("req", "res"), [({"bogus", "baz"}, True),
                                              ({"bogus", "meh"}, False)])
    def test_warn_any(self, req, res):
        tstdic = {"foo": 5, "bar": 2, "baz": 7}
        assert check_keys(tstdic, req, action="warning", all_any="any") is res

    def test_raises_by_default(self):
        tstdic = {"foo": 5, "bar": 2, "baz": 7}
        with pytest.raises(ValueError):
            check_keys(tstdic, {"bogus"})

    def test_raises_for_invalid_any_all(self):
        tstdic = {"foo": 5, "bar": 2, "baz": 7}
        with pytest.raises(ValueError):
            check_keys(tstdic, {"foo"}, all_any="bogus")

    def test_warns_for_bad_type(self):
        tstdic = {"a": 5, "b": 2, "c": 7}
        with pytest.warns(AstarWarning):
            check_keys(tstdic, "abc")
