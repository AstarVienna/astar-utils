# -*- coding: utf-8 -*-
"""General utility function, mostly exported from ScopeSim."""

from warnings import warn
from collections.abc import Iterable, Generator, Set, Mapping

from .exceptions import AstarWarning, AstarUserWarning


def close_loop(iterable: Iterable) -> Generator:
    """
    Add the first element of an iterable to the end again.

    This is useful for e.g. plotting a closed shape from a list of points.

    Parameters
    ----------
    iterable : Iterable
        Input iterable with n elements.

    Yields
    ------
    loop : Generator
        Output iterable with n+1 elements.

    Examples
    --------
    >>> x, y = [1, 2, 3], [4, 5, 6]
    >>> x, y = zip(*close_loop(zip(x, y)))
    >>> x
    (1, 2, 3, 1)
    >>> y
    (4, 5, 6, 4)

    """
    iterator = iter(iterable)
    first = next(iterator)
    yield first
    yield from iterator
    yield first


def stringify_dict(dic: Mapping, allowed_types=(str, int, float, bool)):
    """Turn a dict entries into strings for addition to FITS headers."""
    for key, value in dic.items():
        if isinstance(value, allowed_types):
            yield key, value
        else:
            yield key, str(value)


def check_keys(
    input_dict: Iterable,
    required_keys: Set,
    action: str = "error",
    all_any: str = "all",
) -> bool:
    """
    Check to see if all/any of the required keys are present in a dict.

    Parameters
    ----------
    input_dict : Union[Mapping, Iterable]
        The mapping to be checked.
    required_keys : Set
        Set containing the keys to look for.
    action : {"error", "warn", "warning"}, optional
        What to do in case the check does not pass. The default is "error".
    all_any : {"all", "any"}, optional
        Whether to check if "all" or "any" of the `required_keys` are present.
        The default is "all".

    Raises
    ------
    ValueError
        Raised when an invalid parameter was passed or when `action` was set to
        "error" (the default) and the `required_keys` were not found.

    Returns
    -------
    keys_present : bool
        ``True`` if check succeded, ``False`` otherwise.

    """
    # Checking for Set from collections.abc instead of builtin set to allow
    # for any duck typing (e.g. dict keys view or whatever)
    if not isinstance(required_keys, Set):
        warn("required_keys should implement the Set protocol, found "
             f"{type(required_keys)} instead.", AstarWarning)
        required_keys = set(required_keys)

    if all_any == "all":
        keys_present = required_keys.issubset(input_dict)
    elif all_any == "any":
        keys_present = not required_keys.isdisjoint(input_dict)
    else:
        raise ValueError("all_any must be either 'all' or 'any'")

    if not keys_present:
        missing = "', '".join(required_keys.difference(input_dict)) or "<none>"
        msg = f"The keys '{missing}' are missing from input_dict."
        if "error" in action:
            raise ValueError(msg)
        if "warn" in action:
            warn(msg, AstarUserWarning)

    return keys_present
