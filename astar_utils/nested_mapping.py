# -*- coding: utf-8 -*-
"""Contains NestedMapping class."""

from typing import TextIO, Optional, Union, Any
from io import StringIO
from collections import abc, ChainMap

from more_itertools import ilen

from .loggers import get_logger

logger = get_logger(__name__)


class NestedMapping(abc.MutableMapping):
    # TODO: improve docstring
    """Dictionary-like structure that supports nested !-bang string keys."""

    def __init__(self, new_dict: Optional[abc.Iterable] = None,
                 title: Optional[str] = None):
        self.dic: abc.MutableMapping[str, Any] = {}
        self._title = title
        if isinstance(new_dict, abc.MutableMapping):
            self.update(new_dict)
        elif isinstance(new_dict, abc.Iterable):
            for entry in new_dict:
                self.update(entry)

    def update(self, new_dict: abc.MutableMapping[str, Any]) -> None:
        if isinstance(new_dict, NestedMapping):
            new_dict = new_dict.dic  # Avoid updating with another one

        # TODO: why do we check for dict here but not in the else?
        if isinstance(new_dict, abc.Mapping) and "alias" in new_dict:
            alias = new_dict["alias"]
            propdict = new_dict.get("properties", {})
            if alias in self.dic:
                self.dic[alias] = recursive_update(self.dic[alias], propdict)
            else:
                self.dic[alias] = propdict
        elif isinstance(new_dict, abc.Sequence):
            # To catch list of tuples
            self.update(dict([new_dict]))
        else:
            # Catch any bang-string properties keys
            to_pop = []
            for key in new_dict:
                if is_bangkey(key):
                    logger.debug(
                        "Bang-string key %s was seen in .update. This should "
                        "not occur outside mocking in testing!", key)
                    self[key] = new_dict[key]
                    to_pop.append(key)
            for key in to_pop:
                new_dict.pop(key)

            if len(new_dict) > 0:
                self.dic = recursive_update(self.dic, new_dict)

    def __getitem__(self, key: str):
        """x.__getitem__(y) <==> x[y]."""
        if not is_bangkey(key):
            return self.dic[key]

        key_chunks = self._split_subkey(key)
        entry = self.dic
        for chunk in key_chunks:
            self._guard_submapping(
                entry, key_chunks[:key_chunks.index(chunk)], "get")
            try:
                entry = entry[chunk]
            except KeyError as err:
                raise KeyError(key) from err

        if is_nested_mapping(entry):
            return self.__class__(entry)
        return entry

    def __setitem__(self, key: str, value) -> None:
        """Set self[key] to value."""
        if not is_bangkey(key):
            self.dic[key] = value
            return

        *key_chunks, final_key = self._split_subkey(key)
        entry = self.dic
        for chunk in key_chunks:
            if chunk not in entry:
                entry[chunk] = {}
            entry = entry[chunk]
        self._guard_submapping(entry, key_chunks, "set")
        entry[final_key] = value

    def __delitem__(self, key: str) -> None:
        """Delete self[key]."""
        if not is_bangkey(key):
            del self.dic[key]
            return

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

    @staticmethod
    def _split_subkey(key: str):
        return key.removeprefix("!").split(".")

    @staticmethod
    def _join_subkey(key=None, subkey=None) -> str:
        return f"!{key.removeprefix('!')}.{subkey}" if key is not None else subkey

    @staticmethod
    def _guard_submapping(entry, key_chunks, kind: str = "get") -> None:
        kinds = {"get": "retrieved from like a dict",
                 "set": "overwritten with a new sub-mapping",
                 "del": "be deleted from"}
        submsg = kinds.get(kind, "modified")
        if not isinstance(entry, abc.Mapping):
            raise KeyError(
                f"Bang-key '!{'.'.join(key_chunks)}' doesn't point to a sub-"
                f"mapping but to a single value, which cannot be {submsg}. "
                "To replace or remove the value, call ``del "
                f"self['!{'.'.join(key_chunks)}']`` first and then optionally "
                "re-assign a new sub-mapping to the key.")

    def _staggered_items(self, key: Union[str, None],
                         value: abc.Mapping) -> abc.Iterator[tuple[str, Any]]:
        simple = []
        for subkey, subvalue in value.items():
            new_key = self._join_subkey(key, subkey)
            if isinstance(subvalue, abc.Mapping):
                yield from self._staggered_items(new_key, subvalue)
            else:
                simple.append((new_key, subvalue))
        yield from simple

    def __iter__(self) -> abc.Iterator[str]:
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

    def _write_subitems(self, items: abc.Collection[tuple[str, Any]], pre: str,
                        stream: TextIO, nested: bool = False
                        ) -> list[tuple[str, Any]]:
        # TODO: could this (and _write_subdict) use _staggered_items instead??
        n_items = len(items)
        simple: list[tuple[str, Any]] = []

        for i_sub, (key, val) in enumerate(items):
            is_super = isinstance(val, abc.Mapping)
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

    def _write_subdict(self, subdict: abc.Mapping, stream: TextIO,
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

    def _repr_pretty_(self, printer, cycle):
        """For ipython."""
        if cycle:
            printer.text("NestedMapping(...)")
        else:
            printer.text(str(self))


class RecursiveNestedMapping(NestedMapping):
    """Like NestedMapping but internally resolves any bang-string values.

    In the event of an infinite loop of recursive bang-string keys pointing
    back to each other, this should savely and quickly throw a
    ``RecursionError``.
    """

    def __getitem__(self, key: str):
        """x.__getitem__(y) <==> x[y]."""
        value = super().__getitem__(key)
        while is_bangkey(value):
            try:
                value = self[value]
            except KeyError:
                return value
        return value

    @classmethod
    def from_maps(cls, maps, key):
        """Yield instances from maps if key is found."""
        for i, mapping in enumerate(maps):
            if key in mapping:
                # Don't use .get here to avoid chaining empty mappings
                yield RecursiveNestedMapping(
                    mapping[key], title=f"[{i}] mapping")


class NestedChainMap(ChainMap):
    """Subclass of ``collections.ChainMap`` using ``RecursiveNestedMapping``.

    Only overrides ``__getitem__`` to allow for both recursive bang-string keys
    accross the individual mappings and to "collect" sub-mappings from the same
    bang-key in multiple mappings into a new `NestedChainMap`.

    Also overrides ``__str__`` and provides a ``_repr_pretty_`` for nice output
    to an IPython console.

    In the absence of any nested mappings or bang-string keys, this will work
    like the base class ``collections.ChainMap``, meaning an ordinary ``dict``
    can also be used as one of the individual mappings.

    In the event of an infinite loop of recursive bang-string keys pointing
    back to each other, this should savely and quickly throw a
    ``RecursionError``.
    """

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]."""
        value = super().__getitem__(key)

        if isinstance(value, abc.Mapping):
            submaps = tuple(RecursiveNestedMapping.from_maps(self.maps, key))
            if len(submaps) == 1:
                # Don't need the chain if it's just one...
                return submaps[0]
            return NestedChainMap(*submaps)

        while is_bangkey(value):
            try:
                value = self[value]
            except KeyError:
                return value
        return value


    def __str__(self):
        """Return str(self)."""
        return "\n\n".join(str(mapping) for mapping in self.maps)

    def _repr_pretty_(self, printer, cycle):
        """For ipython."""
        if cycle:
            printer.text("NestedChainMap(...)")
        else:
            printer.text(str(self))


def is_bangkey(key) -> bool:
    """Return ``True`` if the key is a ``str`` and starts with a "!"."""
    return isinstance(key, str) and key.startswith("!")


def is_nested_mapping(mapping) -> bool:
    """Return ``True`` if `mapping` contains any further map as a value."""
    if not isinstance(mapping, abc.Mapping):
        return False
    return any(isinstance(value, abc.Mapping) for value in mapping.values())


def recursive_update(old_dict: abc.MutableMapping,
                     new_dict: abc.Mapping) -> abc.MutableMapping:
    if new_dict is not None:
        for key in new_dict:
            if old_dict is not None and key in old_dict:
                if isinstance(old_dict[key], abc.Mapping):
                    if isinstance(new_dict[key], abc.Mapping):
                        old_dict[key] = recursive_update(old_dict[key],
                                                         new_dict[key])
                    else:
                        logger.warning("Overwriting dict %s with non-dict: %s",
                                       old_dict[key], new_dict[key])
                        old_dict[key] = new_dict[key]
                else:
                    if isinstance(new_dict[key], abc.Mapping):
                        logger.warning("Overwriting non-dict %s with dict: %s",
                                       old_dict[key], new_dict[key])
                    old_dict[key] = new_dict[key]
            else:
                old_dict[key] = new_dict[key]

    return old_dict
