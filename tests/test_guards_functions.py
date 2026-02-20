# -*- coding: utf-8 -*-
"""Unit tests for guard_functions."""

import pytest

from astar_utils.guard_functions import guard_same_len


class TestGuardSameLen():
    def test_nothing(self):
        assert guard_same_len() is None

    def test_one(self):
        assert guard_same_len([1, 2, 3, 4, 5]) is None

    def test_one_none(self):
        assert guard_same_len(None) is None

    def test_all_none(self):
        assert guard_same_len(None, None, None, None) is None

    def test_all_equal(self):
        assert guard_same_len([1, 2, 3], ["foo", "bar", "baz"]) is None

    def test_all_equal_or_none(self):
        assert guard_same_len([1, 2], ["foo", "bar"], None) is None

    def test_all_none_except_one(self):
        assert guard_same_len([1, 2, 3, 4], None, None, None) is None

    def test_all_unequal(self):
        with pytest.raises(ValueError):
            guard_same_len([1, 2], ["foo", "bar", "baz"], range(10))

    def test_all_unequal_or_none(self):
        with pytest.raises(ValueError):
            guard_same_len([1, 2, 3, 4], None, ["foo", "bar"], None)

    def test_one_unequal(self):
        with pytest.raises(ValueError):
            guard_same_len([1, 2], ["foo", "bar"], range(10))

    def test_one_unequal_or_none(self):
        with pytest.raises(ValueError):
            guard_same_len([1, 2], ["foo", "bar"], range(10), None, None)
