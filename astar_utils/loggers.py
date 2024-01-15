# -*- coding: utf-8 -*-
"""To have all logger creation in one place."""

import logging



def get_astar_logger() -> logging.Logger:
    """Get a logger with name "astar"."""
    return logging.getLogger("astar")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with given name as a child of the "astar" logger."""
    return get_astar_logger().getChild(name)

