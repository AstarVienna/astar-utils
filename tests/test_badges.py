# -*- coding: utf-8 -*-
"""Unit tests for badges.py."""

from io import StringIO

import yaml
import pytest

from astar_utils.badges import (BadgeReport, Badge, BoolBadge, NumBadge,
                                StrBadge, MsgOnlyBadge, make_entries)
from astar_utils.nested_mapping import NestedMapping


@pytest.fixture(name="temp_dir", scope="module")
def fixture_temp_dir(tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("PKG_DIR")
    (tmpdir / "_REPORTS").mkdir()
    return tmpdir


class TestBadgeSubclasses:
    def test_bool(self):
        assert isinstance(Badge("bogus", True), BoolBadge)
        assert isinstance(Badge("bogus", False), BoolBadge)

    def test_num(self):
        assert isinstance(Badge("bogus", 7), NumBadge)
        assert isinstance(Badge("bogus", 3.14), NumBadge)

    def test_str(self):
        assert isinstance(Badge("bogus", "foo"), StrBadge)

    def test_msgonly(self):
        assert isinstance(Badge("bogus", "!foo"), MsgOnlyBadge)

    def test_raises_for_invalid(self):
        with pytest.raises(TypeError):
            Badge("foo", [2, 3])


class TestColours:
    @pytest.mark.parametrize("value, colour", [
        ("observation", "blueviolet"),
        ("support", "deepskyblue"),
        ("error", "red"),
        ("missing", "red"),
        ("warning", "orange"),
        ("conflict", "orange"),
        ("incomplete", "orange"),
        ("ok", "green"),
        ("found", "green"),
        ("not_found", "red"),
        ("none", "yellowgreen"),
    ])
    def test_special_strings(self, value, colour):
        assert Badge("bogus", value).colour == colour

    def test_bool(self):
        assert Badge("bogus", True).colour == "green"
        assert Badge("bogus", False).colour == "red"

    def test_num(self):
        assert Badge("bogus", 7).colour == "lightblue"


class TestPattern:
    def test_simple(self):
        with StringIO() as str_stream:
            Badge("bogus", "Error").write(str_stream)
            pattern = "[![](https://img.shields.io/badge/bogus-Error-red)]()"
            assert pattern in str_stream.getvalue()

    def test_msg_only(self):
        with StringIO() as str_stream:
            Badge("bogus", "!OK").write(str_stream)
            pattern = "[![](https://img.shields.io/badge/bogus-green)]()"
            assert pattern in str_stream.getvalue()


class TestSpecialChars:
    def test_space(self):
        badge = Badge("bogus foo", "bar baz")
        assert badge.key == "bogus_foo"
        assert badge.value == "bar_baz"

    def test_dash(self):
        badge = Badge("bogus-foo", "bar-baz")
        assert badge.key == "bogus--foo"
        assert badge.value == "bar--baz"


class TestReport:
    # TODO: the repeated setup stuff should be a fixture or something I guess

    @pytest.mark.usefixtures("temp_dir")
    def test_writes_yaml(self, temp_dir):
        path = temp_dir / "_REPORTS"
        with BadgeReport("test.yaml", "test.md", base_path=path) as report:
            report["!foo.bar"] = "bogus"
        assert (temp_dir / "_REPORTS/test.yaml").exists()

    @pytest.mark.usefixtures("temp_dir")
    def test_writes_md(self, temp_dir):
        path = temp_dir / "_REPORTS"
        with BadgeReport("test.yaml", "test.md", base_path=path) as report:
            report["!foo.bar"] = "bogus"
        assert (temp_dir / "_REPORTS/test.md").exists()

    @pytest.mark.usefixtures("temp_dir")
    def test_yaml_content(self, temp_dir):
        path = temp_dir / "_REPORTS"
        with BadgeReport("test.yaml", "test.md", base_path=path) as report:
            report["!foo.bar"] = "bogus"
        path = temp_dir / "_REPORTS/test.yaml"
        with path.open(encoding="utf-8") as file:
            dic = NestedMapping(yaml.full_load(file))
            assert "!foo.bar" in dic
            assert dic["!foo.bar"] == "bogus"

    @pytest.mark.usefixtures("temp_dir")
    def test_md_content(self, temp_dir):
        path = temp_dir / "_REPORTS"
        with BadgeReport("test.yaml", "test.md", base_path=path) as report:
            report["!foo.bar"] = "bogus"
        file = path / "test.md"
        markdown = file.read_text(encoding="utf-8")
        assert "## foo" in markdown
        badge = "[![](https://img.shields.io/badge/bar-bogus-lightgrey)]()"
        assert badge in markdown

    def test_inits_dir_if_missing(self):
        report = BadgeReport()
        assert report.yamlpath.parts[-2] == "_REPORTS"


class TestMakeEntries:
    def test_does_nothing_if_not_mapping(self):
        with StringIO() as str_stream:
            make_entries(str_stream, "foo")
            assert str_stream.getvalue() == ""

    def test_nested(self):
        dic = {"a": {"foo": 1, "bar": 2, "baz": {"x": "a", "y": "b"}}}
        with StringIO() as str_stream:
            make_entries(str_stream, dic)
            output = str_stream.getvalue()

        assert "## a\n" in output
        assert "### Baz\n* " in output

    def test_very_nested(self):
        dic = {"a": {"b": {"c": {"d": {"e": "f"}}}}}
        with StringIO() as str_stream:
            make_entries(str_stream, dic)
            output = str_stream.getvalue()

        assert "## a\n### B\n#### C\n  * d: \n    * " in output
        assert "e-f" in output

    @pytest.mark.parametrize("dic", [
        {"a": {"foo": 1, "bar": 2}},
        {"a": {"baz": {"x": "a", "y": "b"}, "foo": 1, "bar": 2},
         "b": {"x": 42}, "bogus": "yeet"},
    ])
    def test_works_with_nested_mapping(self, dic):
        with StringIO() as str_stream:
            make_entries(str_stream, dic)
            output1 = str_stream.getvalue()

        with StringIO() as str_stream:
            make_entries(str_stream, NestedMapping(dic))
            output2 = str_stream.getvalue()

        assert output2 == output1
