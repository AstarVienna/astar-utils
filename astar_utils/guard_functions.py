# -*- coding: utf-8 -*-
"""Various small checkers."""


def guard_same_len(*args):
    """Check if all args are the same len or None, raise otherwise."""
    n_lens = len(set(len(arg) for arg in args if arg is not None))
    if n_lens > 1:
        raise ValueError(
            f"Arguments must have equal length or be None, found {n_lens-1} "
            "mismatching argument lengths."
        )
