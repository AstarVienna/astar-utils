# -*- coding: utf-8 -*-
"""To have all logger creation in one place."""

import logging


def get_logger(name: str):
    """Get a logger with given name as a child of the "astar" logger."""
    return logging.getLogger("astar").getChild(name)
