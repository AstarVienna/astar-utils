# -*- coding: utf-8 -*-
"""Unit tests for loggers.py."""

import logging
from importlib import reload
from io import StringIO

import pytest

from astar_utils.loggers import get_astar_logger, get_logger, ColoredFormatter


@pytest.fixture(scope="class", autouse=True)
def reset_logging():
    logging.shutdown()
    reload(logging)
    yield
    logging.shutdown()


@pytest.fixture(scope="class")
def base_logger():
    return get_astar_logger()


@pytest.fixture(scope="class")
def child_logger():
    return get_logger("test")


class TestBaseLogger:
    def test_name(self, base_logger):
        assert base_logger.name == "astar"

    def test_parent(self, base_logger):
        assert base_logger.parent.name == "root"

    def test_initial_level(self, base_logger):
        assert base_logger.level == 0

    def test_has_no_handlers(self, base_logger):
        assert not base_logger.handlers


class TestChildLogger:
    def test_name(self, child_logger):
        assert child_logger.name == "astar.test"

    def test_parent(self, child_logger):
        assert child_logger.parent.name == "astar"

    def test_initial_level(self, child_logger):
        assert child_logger.level == 0

    def test_has_no_handlers(self, child_logger):
        assert not child_logger.handlers

    def test_level_propagates(self, base_logger, child_logger):
        base_logger.setLevel("ERROR")
        assert child_logger.getEffectiveLevel() == 40


class TestColoredFormatter:
    def test_repr(self):
        assert f"{ColoredFormatter()!r}" == "<ColoredFormatter>"

    def test_levels_are_ints(self):
        colf = ColoredFormatter()
        assert isinstance(colf.show_level, int)
        assert isinstance(colf.bright_level, int)
        for key in colf.colors:
            assert isinstance(key, int)

    def test_colors_are_valid(self):
        colf = ColoredFormatter()
        for value in colf.colors.values():
            assert value.startswith("\x1b[")

    @pytest.mark.parametrize("level",
                             ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
    def test_colors_are_in_log_msg(self, level, base_logger,
                                   child_logger, caplog):
        with StringIO() as str_stream:
            # need string stream handler to capture color codes
            handler1 = logging.StreamHandler(stream=str_stream)
            handler2 = logging.StreamHandler()  # sys.stdout
            handler1.setFormatter(ColoredFormatter())
            handler2.setFormatter(ColoredFormatter())
            handler1.setLevel(logging.DEBUG)
            handler2.setLevel(logging.DEBUG)
            base_logger.addHandler(handler1)
            base_logger.addHandler(handler2)
            base_logger.propagate = True
            base_logger.setLevel(logging.DEBUG)

            int_level = logging.getLevelNamesMapping()[level]
            print(f"\nTest logging level: {level}:")
            child_logger.log(int_level, "foo")

            # release the handler to avoid I/O on closed stream errors
            base_logger.removeHandler(handler1)
            base_logger.removeHandler(handler2)
            del handler1
            del handler2

            assert level in caplog.text
            assert "foo" in caplog.text
            assert "astar.test" in caplog.text

            # caplog.text seems to strip the color codes...
            colored_text = str_stream.getvalue()
            assert colored_text.startswith("\x1b[")
            assert colored_text.strip().endswith("\x1b[0m")
