# -*- coding: utf-8 -*-
"""Unit tests for unique_list.py."""

import pytest

from astar_utils.unique_list import UniqueList


@pytest.fixture
def simple_unilst():
    inlist = ["foo", "bar", "baz"]
    return UniqueList(inlist)


class TestSimpleListOperations:
    def test_init_empty_and_append_items(self):
        unilst = UniqueList()
        assert not len(unilst)
        unilst.append("foo")
        unilst.append("bar")
        assert unilst[0] == "foo"
        assert unilst[1] == "bar"

    @pytest.mark.parametrize("inlist", [[1, 2, 3], ["a", "b", "c"]])
    def test_stores_simple_input_list(self, inlist):
        unilst = UniqueList(inlist)
        assert all(item in unilst for item in inlist)

    def test_items_can_be_retrieved(self):
        inlist = ["foo", "bar", "baz"]
        unilst = UniqueList(inlist)
        assert unilst[1] == inlist[1]

    def test_item_mutation_raises_error(self, simple_unilst):
        with pytest.raises(TypeError):
            simple_unilst[1] = "bogus"

    def test_can_insert_item_at_location(self, simple_unilst):
        simple_unilst.insert(1, "bogus")
        assert simple_unilst[1] == "bogus"

    def test_can_delete_items(self, simple_unilst):
        assert simple_unilst[0] == "foo"
        assert len(simple_unilst) == 3
        del simple_unilst[0]
        assert "foo" not in simple_unilst
        assert len(simple_unilst) == 2
        assert simple_unilst[-1] == "baz"
        simple_unilst.remove("baz")
        assert "baz" not in simple_unilst
        assert len(simple_unilst) == 1

    def test_repr_produces_correct_str(self, simple_unilst):
        assert f"{simple_unilst!r}" == "UniqueList(['foo', 'bar', 'baz'])"

    def test_str_uses_repr(self, simple_unilst):
        assert f"{simple_unilst!s}" == "UniqueList(['foo', 'bar', 'baz'])"


class TestUniqueness:
    @pytest.mark.parametrize("inlist", [[1, 2, 1], ["a", "b", "c", "c", "c"]])
    def test_doesnt_store_duplicates(self, inlist):
        unilst = UniqueList(inlist)
        assert len(unilst) == len(set(inlist))

    @pytest.mark.parametrize("inlist", [[3, 1, 2], ["c", "b", "a"]])
    def test_order_is_maintained(self, inlist):
        unilst = UniqueList(inlist)
        assert list(unilst) == inlist

    def test_duplicates_use_first_occurance(self):
        unilst = UniqueList(["foo", "bar", "bar", "baz", "foo"])
        assert list(unilst) == ["foo", "bar", "baz"]

    def test_append_first_works(self, simple_unilst):
        assert simple_unilst[0] == "foo"
        assert len(simple_unilst) == 3
        simple_unilst.append_first("bogus")
        assert simple_unilst[0] == "bogus"
        assert simple_unilst[1] == "foo"
        assert len(simple_unilst) == 4

    def test_append_first_moves_existing_item(self, simple_unilst):
        assert list(simple_unilst) == ["foo", "bar", "baz"]
        simple_unilst.append_first("bar")
        assert list(simple_unilst) == ["bar", "foo", "baz"]


class TestOtherListMethods:
    def test_pop(self, simple_unilst):
        popped = simple_unilst.pop(-1)
        assert popped == "baz"
        assert "baz" not in simple_unilst

    def test_extend(self, simple_unilst):
        simple_unilst.extend(["bar", "bogus", "foo", "bogus"])
        assert list(simple_unilst) == ["foo", "bar", "baz", "bogus"]

    def test_iadd(self, simple_unilst):
        simple_unilst += ["bar", "bogus", "foo", "bogus"]
        assert list(simple_unilst) == ["foo", "bar", "baz", "bogus"]

    def test_reverse_throws(self, simple_unilst):
        # TODO: should it though?
        with pytest.raises(TypeError):
            simple_unilst.reverse()
