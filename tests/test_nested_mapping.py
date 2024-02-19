# -*- coding: utf-8 -*-
"""Unit tests for nested_mapping.py."""

from unittest.mock import Mock

import pytest
import yaml

from astar_utils.nested_mapping import (NestedMapping, RecursiveNestedMapping,
                                        NestedChainMap, recursive_update,
                                        is_bangkey, is_nested_mapping)

_basic_yaml = """
alias : OBS
properties :
    temperature : 100
"""


@pytest.fixture
def basic_yaml():
    return yaml.full_load(_basic_yaml)


@pytest.fixture
def basic_nestmap(basic_yaml):
    return NestedMapping(basic_yaml)


@pytest.fixture
def nested_dict():
    return {"foo": 5, "bar": {"bogus": {"a": 42, "b": 69},
                              "baz": "meh"},
            "moo": "yolo",
            "yeet": {"x": 0, "y": 420}}


@pytest.fixture
def nested_nestmap(nested_dict):
    return NestedMapping(nested_dict)


@pytest.fixture
def simple_nestchainmap():
    ncm = NestedChainMap(
        RecursiveNestedMapping({"foo": {"a": "!foo.b"}}),
        RecursiveNestedMapping({"foo": {"b": "bogus", "c": "baz"}})
    )
    return ncm


class TestInit:
    def test_initialises_with_nothing(self):
        nestmap = NestedMapping()
        assert isinstance(nestmap, NestedMapping)
        assert nestmap.title == "NestedMapping"

    def test_initalises_with_normal_dict(self):
        nestmap = NestedMapping({"a": 1, "b": 2})
        assert isinstance(nestmap, NestedMapping)

    def test_initalises_with_list_of_tuples(self):
        nestmap = NestedMapping([("a", 1), ("b", 2)])
        assert isinstance(nestmap, NestedMapping)

    def test_initalises_with_basic_yaml_dict(self, basic_nestmap):
        assert isinstance(basic_nestmap, NestedMapping)
        assert "OBS" in basic_nestmap.dic

    def test_initalises_with_nested_dict(self, nested_nestmap):
        assert isinstance(nested_nestmap, NestedMapping)
        assert "moo" in nested_nestmap.dic

    def test_init_with_title(self, basic_yaml):
        nestmap = NestedMapping(basic_yaml, title="MyNestMap")
        assert nestmap.title == "MyNestMap"


class TestActsLikeDict:
    def test_can_add_and_retrieve_normal_dict_entries(self):
        nestmap = NestedMapping()
        nestmap["name"] = "ELT"
        assert nestmap["name"] == "ELT"

    def test_can_and_and_retrieve_special_dict_entries(self, basic_nestmap):
        basic_nestmap["!OBS.lam.max.unit"] = "um"
        assert basic_nestmap["!OBS.lam.max.unit"] == "um"
        assert basic_nestmap["!OBS.temperature"] == 100

    def test_returns_another_nestmap_for_subdict(self, nested_nestmap):
        assert isinstance(nested_nestmap["!bar"], NestedMapping)

    def test_uses___contains___keyword_for_normal_dicts(self):
        nestmap = NestedMapping({"name": "ELT"})
        assert "name" in nestmap

    def test_uses___contains___keyword_for_special_dicts(self, basic_nestmap):
        assert "!OBS.temperature" in basic_nestmap
        assert "!OBS.temperature.unit" not in basic_nestmap
        assert "!OBS.humidity" not in basic_nestmap

    def test_can_delete_simple_key(self, nested_nestmap):
        assert "foo" in nested_nestmap
        del nested_nestmap["foo"]
        assert "foo" not in nested_nestmap

    def test_can_delete_nested_key(self, nested_nestmap):
        key = "!bar.bogus.b"
        assert nested_nestmap[key] == 69
        del nested_nestmap[key]
        with pytest.raises(KeyError) as excinfo:
            nested_nestmap[key]
        assert key in str(excinfo.value)

    @pytest.mark.parametrize(["key", "full_err"],
                             [("bogus", False),
                              ("!foo.bogus", True),
                              ("!yeet.x.l.m", True),
                              ("!yeet.z.l.m", False)])
    def test_throws_when_deleting_nonexisting_key(self, key, full_err,
                                                  nested_nestmap):
        with pytest.raises(KeyError) as excinfo:
            del nested_nestmap[key]
        if full_err:
            assert "deleted from" in str(excinfo.value)
        else:
            assert key in str(excinfo.value)

    def test_throws_when_setting_value_to_subdict(self, nested_nestmap):
        with pytest.raises(KeyError) as excinfo:
            nested_nestmap["!foo.bogus"] = 3
        assert "overwritten with" in str(excinfo.value)


class TestRecursiveUpdate:
    def test_updates_normal_recursive_dicts(self):
        nestmap = NestedMapping()
        nestmap["name"] = {"value": "ELT"}
        nestmap.update({"name": {"type": "str"}})
        assert nestmap["name"]["value"] == "ELT"
        assert nestmap["name"]["type"] == "str"

    def test_updates_yaml_alias_recursive_dicts(self, basic_nestmap,
                                                basic_yaml):
        basic_yaml["properties"] = {"temperature": 42, "humidity": 0.75}
        basic_nestmap.update(basic_yaml)
        assert basic_nestmap["!OBS.temperature"] == 42
        assert basic_nestmap["OBS"]["humidity"] == 0.75

    def test_updates_yaml_bang_properties_dicts(self, basic_nestmap,
                                                basic_yaml):
        basic_nestmap.update({"!SIM.someglobal": True})
        assert basic_nestmap["!SIM.someglobal"]


class TestFunctionRecursiveUpdate:
    def test_recursive_update_combines_dicts(self):
        e = {"a": {"b": {"c": 1}}}
        f = {"a": {"b": {"d": 2}}}
        recursive_update(e, f)
        assert e["a"]["b"]["c"] == 1
        assert e["a"]["b"]["d"] == 2

    def test_recursive_update_overwrites_scalars(self):
        e = {"a": {"b": {"c": 1}}}
        f = {"a": {"b": {"c": 2}}}
        recursive_update(e, f)
        assert e["a"]["b"]["c"] == 2

    def test_recursive_update_overwrites_dict_with_scalar(self):
        e = {"a": {"b": {"c": 1}}}
        f = {"a": {"b": 4}}
        recursive_update(e, f)
        assert e["a"]["b"] == 4

    def test_recursive_update_overwrites_scalar_with_dict(self):
        e = {"a": {"b": 5}}
        f = {"a": {"b": {"c": 1}}}
        recursive_update(e, f)
        assert e["a"]["b"] == {"c": 1}

    def test_recursive_update_overwrites_string_with_string(self):
        e = {"a": {"b": {"c": "hello"}}}
        f = {"a": {"b": {"c": "world"}}}
        recursive_update(e, f)
        assert e["a"]["b"]["c"] == "world"


class TestRepresentation:
    def test_str_conversion(self, nested_nestmap):
        desired = """
NestedMapping contents:
├─bar: 
│ ├─bogus: 
│ │ ├─a: 42
│ │ └─b: 69
│ └─baz: meh
├─yeet: 
│ ├─x: 0
│ └─y: 420
├─foo: 5
└─moo: yolo
""".strip()
        assert str(nested_nestmap) == desired

    def test_repr_conversion(self, nested_nestmap):
        desired = ("NestedMapping({'foo': 5, 'bar': {'bogus': "
                   "{'a': 42, 'b': 69}, 'baz': 'meh'}, 'moo': 'yolo', "
                   "'yeet': {'x': 0, 'y': 420}})")
        assert nested_nestmap.__repr__() == desired

    def test_len_works(self, nested_nestmap):
        assert len(nested_nestmap) == 7

    def test_list_returns_keys(self, nested_nestmap):
        desired = ["!bar.bogus.a", "!bar.bogus.b", "!bar.baz", "!yeet.x",
                   "!yeet.y", "foo", "moo"]
        assert list(nested_nestmap) == desired

    def test_title_is_in_str(self, basic_yaml):
        nestmap = NestedMapping(basic_yaml, title="MyNestMap")
        assert "MyNestMap" in str(nestmap)

    def test_repr_pretty(self, nested_nestmap):
        printer = Mock()
        nested_nestmap._repr_pretty_(printer, True)
        printer.text.assert_called_with("NestedMapping(...)")
        nested_nestmap._repr_pretty_(printer, False)
        printer.text.assert_called_with(str(nested_nestmap))


class TestRecursiveNestedMapping:
    def test_resolves_bangs(self):
        rnm = RecursiveNestedMapping(
            {"foo": {
                "a": "!bar.x",
                "b": "!bar.y",
              },
             "bar": {
                 "x": 42,
                 "y": "!foo.a",
              },
             })
        assert rnm["!foo.b"] == 42

    def test_infinite_loop(self):
        rnm = RecursiveNestedMapping(
            {"foo": {
                "a": "!bar.x",
                "b": "!bar.y",
              },
             "bar": {
                 "x": "!foo.b",
                 "y": "!foo.a",
              },
             })
        with pytest.raises(RecursionError):
            rnm["!foo.b"]

    def test_returns_unresolved_as_is(self):
        rnm = RecursiveNestedMapping(
            {"foo": {
                "a": "!bar.x",
                "b": "!bar.y",
              },
             })
        assert rnm["!foo.b"] == "!bar.y"


class TestNestedChainMap:
    def test_resolves_bangs(self, simple_nestchainmap):
        assert simple_nestchainmap["!foo.a"] == "bogus"

    def test_infinite_loop(self):
        ncm = NestedChainMap(
            RecursiveNestedMapping({"foo": {"a": "!foo.b"}}),
            RecursiveNestedMapping({"foo": {"b": "!foo.a"}})
        )
        with pytest.raises(RecursionError):
            ncm["!foo.a"]

    def test_repr_pretty(self, simple_nestchainmap):
        printer = Mock()
        simple_nestchainmap._repr_pretty_(printer, True)
        printer.text.assert_called_with("NestedChainMap(...)")
        simple_nestchainmap._repr_pretty_(printer, False)
        printer.text.assert_called_with(str(simple_nestchainmap))


class TestNestedChainMapSubdictKeyInMultipleLevels:
    def test_returns_chainmap_if_found_in_multiple(self, simple_nestchainmap):
        assert isinstance(simple_nestchainmap["foo"], NestedChainMap)

    def test_subdict_chainmap_has_correct_len(self, simple_nestchainmap):
        assert len(simple_nestchainmap["foo"]) == 3

    def test_returns_nestmap_if_found_in_only_one(self):
        ncm = NestedChainMap(
            RecursiveNestedMapping({"foo": {"a": "!foo.b"}}),
            RecursiveNestedMapping({"bar": {"b": "bogus", "c": "baz"}})
        )
        assert isinstance(ncm["foo"], RecursiveNestedMapping)


@pytest.mark.parametrize(("key", "result"),
                         [("!foo", True),
                          ("bar", False),
                          (42, False)]
                         )
def test_is_bangkey(key, result):
    assert is_bangkey(key) == result


@pytest.mark.parametrize(("mapping", "result"),
                         [({"a": 5, "b": {"x": 2, "y": 3}}, True),
                          ({"a": 5, "b": 7}, False),
                          ("bogus", False),
                          (42, False)]
                         )
def test_is_nested_mapping(mapping, result):
    assert is_nested_mapping(mapping) == result
