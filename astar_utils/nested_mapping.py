# -*- coding: utf-8 -*-
"""Contains NestedMapping class."""

import logging
from typing import TextIO
from io import StringIO
from collections.abc import Iterable, Mapping, MutableMapping

from more_itertools import ilen


class NestedMapping(MutableMapping):
    # TODO: improve docstring
    """Dictionary-like structure that supports nested !-bang string keys."""

    def __init__(self, new_dict: Iterable = None):
        self.dic = {}
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
        else:
            # Catch any bang-string properties keys
            to_pop = []
            for key in new_dict:
                if key.startswith("!"):
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
                if not isinstance(entry, Mapping):
                    raise KeyError(chunk)
                entry = entry[chunk]
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
            entry[final_key] = value
        else:
            self.dic[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete self[key]."""
        if isinstance(key, str) and key.startswith("!"):
            *key_chunks, final_key = self._split_subkey(key)
            entry = self.dic
            for chunk in key_chunks:
                if not isinstance(entry, Mapping):
                    raise KeyError(chunk)
                entry = entry[chunk]
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

    def _yield_subkeys(self, key: str, value: Mapping):
        # TODO: py39: -> Iterator[str]
        for subkey, subvalue in value.items():
            if isinstance(subvalue, Mapping):
                new_key = self._join_subkey(key, subkey)
                yield from self._yield_subkeys(new_key, subvalue)
            else:
                yield self._join_subkey(key, subkey)

    def __iter__(self):
        # TODO: py39: -> Iterator[str]
        """Implement iter(self)."""
        yield from self._yield_subkeys(None, self.dic)

    def __len__(self) -> int:
        """Return len(self)."""
        return ilen(iter(self))

    def _write_subdict(self, subdict: Mapping, stream: TextIO,
                       pad: str = "") -> None:
        pre = pad.replace("├─", "│ ").replace("└─", "  ")
        n_sub = len(subdict)
        for i_sub, (key, val) in enumerate(subdict.items()):
            subpre = "└─" if i_sub == n_sub - 1 else "├─"
            stream.write(f"{pre}{subpre}{key}: ")
            if isinstance(val, Mapping):
                self._write_subdict(val, stream, pre + subpre)
            else:
                stream.write(f"{val}")

    def write_string(self, stream: TextIO) -> None:
        """Write formatted string representation to I/O stream."""
        stream.write(f"{self.__class__.__name__} contents:")
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
