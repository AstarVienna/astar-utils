# -*- coding: utf-8 -*-
"""Exceptions (Errors and Warning) subclasses for use in astar projects.

Inspirations for AstarWarning and AstarUserWarning are taken from the same
concept in Astropy.
"""


class AstarWarning(Warning):
    """The base warning class from which all Astar warnings should inherit."""


class AstarUserWarning(UserWarning, AstarWarning):
    """
    The primary warning class for Astar.

    Use this if you do not need a specific sub-class.
    """
