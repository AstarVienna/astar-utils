# -*- coding: utf-8 -*-
"""Contains UniqueList class."""

from collections.abc import Iterable, MutableSequence


class UniqueList(MutableSequence):
    """Ordered collection with unique elements."""

    def __init__(self, initial: Iterable = None):
        self._set = set()  # For uniqueness
        self._list = []    # For order

        if initial is not None:
            self.extend(initial)

    def __getitem__(self, index: int):
        return self._list[index]

    def __setitem__(self, index: int, value) -> None:
        raise TypeError(
            f"{self.__class__.__name__} does not support item mutation, only "
            "insertion, removal and reordering.")

    def __delitem__(self, index: int) -> None:
        self._set.discard(self._list.pop(index))

    def __len__(self) -> int:
        return len(self._set)

    def __contains__(self, value) -> bool:
        return value in self._set

    def insert(self, index: int, value) -> None:
        if value not in self:
            self._set.add(value)
            self._list.insert(index, value)

    def append_first(self, value) -> None:
        """
        Append element to the front of the list.

        If the element is already present in the list, move it to the front.
        """
        if value in self:
            self.remove(value)
        self.insert(0, value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._list!r})"
