# -*- coding: utf-8 -*-
"""Contains NestedMapping class."""

import logging
from typing import TextIO
from io import StringIO
from collections.abc import Iterable, Sequence, Mapping, MutableMapping

from more_itertools import ilen


class NestedMapping(MutableMapping):
    # TODO: improve docstring
    """Dictionary-like structure that supports nested !-bang string keys."""

    def __init__(self, new_dict: Iterable = None, title: str = None):
        self.dic = {}
        self._title = title
        if isinstance(new_dict, MutableMapping):
            self.update(new_dict)
        elif isinstance(new_dict, Iterable):
            for entry in new_dict:
                self.update(entry)

    def update(self, new_dict: MutableMapping) -> None:
        # TODO: why do we check for dict here but not in the else?
        if isinstance(new_dict, Mapping) \
                and "alias" in new_dict \
                and "properties" in new_dict:
            alias = new_dict["alias"]
            if alias in self.dic:
                self.dic[alias] = recursive_update(self.dic[alias],
                                                   new_dict["properties"])
            else:
                self.dic[alias] = new_dict["properties"]
        elif isinstance(new_dict, Sequence):
            # To catch list of tuples
            self.update(dict([new_dict]))
        else:
            # Catch any bang-string properties keys
            to_pop = []
            for key in new_dict:
                if key.startswith("!"):
                    logging.warning(
                        "Using bang-strings in KEYS is deprecated and will no "
                        "longer work in future releases: %s", key)
                    self[key] = new_dict[key]
                    to_pop.append(key)
            for key in to_pop:
                new_dict.pop(key)

            if len(new_dict) > 0:
                self.dic = recursive_update(self.dic, new_dict)

    def __getitem__(self, key: str):
        """x.__getitem__(y) <==> x[y]."""
        if isinstance(key, str) and key.startswith("!"):
            key_chunks = self._split_subkey(key)
            entry = self.dic
            for chunk in key_chunks:
                self._guard_submapping(
                    entry, key_chunks[:key_chunks.index(chunk)], "get")
                try:
                    entry = entry[chunk]
                except KeyError as err:
                    raise KeyError(key) from err
            return entry
        return self.dic[key]

    def __setitem__(self, key: str, value) -> None:
        """Set self[key] to value."""
        if isinstance(key, str) and key.startswith("!"):
            *key_chunks, final_key = self._split_subkey(key)
            entry = self.dic
            for chunk in key_chunks:
                if chunk not in entry:
                    entry[chunk] = {}
                entry = entry[chunk]
            self._guard_submapping(entry, key_chunks, "set")
            entry[final_key] = value
        else:
            self.dic[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete self[key]."""
        if isinstance(key, str) and key.startswith("!"):
            *key_chunks, final_key = self._split_subkey(key)
            entry = self.dic
            for chunk in key_chunks:
                self._guard_submapping(
                    entry, key_chunks[:key_chunks.index(chunk)], "del")
                try:
                    entry = entry[chunk]
                except KeyError as err:
                    raise KeyError(key) from err
            self._guard_submapping(entry, key_chunks, "del")
            del entry[final_key]
        else:
            del self.dic[key]

    @staticmethod
    def _split_subkey(key: str):
        # TODO: py39: item.removeprefix("!")
        return key[1:].split(".")

    @staticmethod
    def _join_subkey(key=None, subkey=None) -> str:
        # TODO: py39: item.removeprefix("!")
        return f"!{key.strip('!')}.{subkey}" if key is not None else subkey

    @staticmethod
    def _guard_submapping(entry, key_chunks, kind: str = "get") -> None:
        kinds = {"get": "retrieved from like a dict",
                 "set": "overwritten with a new sub-mapping",
                 "del": "be deleted from"}
        submsg = kinds.get(kind, "modified")
        if not isinstance(entry, Mapping):
            raise KeyError(
                f"Bang-key '!{'.'.join(key_chunks)}' doesn't point to a sub-"
                f"mapping but to a single value, which cannot be {submsg}. "
                "To replace or remove the value, call ``del "
                f"self['!{'.'.join(key_chunks)}']`` first and then optionally "
                "re-assign a new sub-mapping to the key.")

    def _staggered_items(self, key: str, value: Mapping):
        # TODO: py39: -> Iterator[tuple[str, Any]]
        simple = []
        for subkey, subvalue in value.items():
            new_key = self._join_subkey(key, subkey)
            if isinstance(subvalue, Mapping):
                yield from self._staggered_items(new_key, subvalue)
            else:
                simple.append((new_key, subvalue))
        yield from simple

    def __iter__(self):
        # TODO: py39: -> Iterator[str]
        """Implement iter(self)."""
        yield from (item[0] for item in self._staggered_items(None, self.dic))

    def __len__(self) -> int:
        """Return len(self)."""
        return ilen(iter(self))

    @staticmethod
    def _write_subkey(key: str, pre: str, final: bool, stream: TextIO) -> str:
        subpre = "└─" if final else "├─"
        newpre = pre + subpre
        stream.write(f"{newpre}{key}: ")
        return newpre

    def _write_subitems(self, items, pre: str,
                        stream: TextIO, nested: bool = False):
        # TODO: py39: items: Iterable[tuple[str, Any]]
        # TODO: py39: -> list[tuple[str, Any]]
        # TODO: could this (and _write_subdict) use _staggered_items instead??
        n_items = len(items)
        simple = []

        for i_sub, (key, val) in enumerate(items):
            is_super = isinstance(val, Mapping)
            if not nested or is_super:
                final = i_sub == n_items - 1 and not simple
                newpre = self._write_subkey(key, pre, final, stream)
            else:
                simple.append((key, val))
                continue

            if nested and is_super:
                self._write_subdict(val, stream, newpre)
            else:
                stream.write(f"{val}")

        return simple

    def _write_subdict(self, subdict: Mapping, stream: TextIO,
                       pad: str = "") -> None:
        pre = pad.replace("├─", "│ ").replace("└─", "  ")
        simple = self._write_subitems(subdict.items(), pre, stream, True)
        self._write_subitems(simple, pre, stream)

    def write_string(self, stream: TextIO) -> None:
        """Write formatted string representation to I/O stream."""
        stream.write(f"{self.title} contents:")
        self._write_subdict(self.dic, stream, "\n")

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"{self.__class__.__name__}({self.dic!r})"

    def __str__(self) -> str:
        """Return str(self)."""
        with StringIO() as str_stream:
            self.write_string(str_stream)
            output = str_stream.getvalue()
        return output

    @property
    def title(self) -> str:
        """Return title if set, or default to class name."""
        return self._title or self.__class__.__name__


def recursive_update(old_dict: MutableMapping, new_dict: Mapping) -> MutableMapping:
    if new_dict is not None:
        for key in new_dict:
            if old_dict is not None and key in old_dict:
                if isinstance(old_dict[key], Mapping):
                    if isinstance(new_dict[key], Mapping):
                        old_dict[key] = recursive_update(old_dict[key],
                                                         new_dict[key])
                    else:
                        logging.warning("Overwriting dict: %s with non-dict: %s",
                                        old_dict[key], new_dict[key])
                        old_dict[key] = new_dict[key]
                else:
                    if isinstance(new_dict[key], Mapping):
                        logging.warning("Overwriting non-dict: %s with dict: %s",
                                        old_dict[key], new_dict[key])
                    old_dict[key] = new_dict[key]
            else:
                old_dict[key] = new_dict[key]

    return old_dict
