# -*- coding: utf-8 -*-
"""."""

import re
from typing import ClassVar
from dataclasses import dataclass, field, InitVar


@dataclass(frozen=True)
class SpectralType:
    """TBA."""

    spectral_class: str | None = field(init=False, default=None)
    spectral_subclass: float | None = field(init=False, default=None)
    luminosity_class: str | None = field(init=False, default=None)
    spectype: InitVar[str]
    _cls_order: ClassVar = "OBAFGKM"  # descending Teff
    _regex: ClassVar = re.compile(
        r"^(?P<spec_cls>[OBAFGKM])(?P<sub_cls>\d(?:\.\d)?)?"
        "(?P<lum_cls>I{1,3}|IV|V)?$", re.A | re.I)

    def __post_init__(self, spectype) -> None:
        """Validate input and populate fields."""
        if not (match := self._regex.fullmatch(spectype)):
            raise ValueError(spectype)

        classes = match.groupdict()
        # Circumvent frozen as per the docs...
        object.__setattr__(self, "spectral_class", classes["spec_cls"])
        object.__setattr__(self, "luminosity_class", classes["lum_cls"])

        if classes["sub_cls"] is not None:
            object.__setattr__(self, "spectral_subclass",
                               float(classes["sub_cls"]))

    @property
    def _subcls_str(self) -> str:
        if self.spectral_subclass is None:
            return ""
        if self.spectral_subclass.is_integer():
            return str(int(self.spectral_subclass))
        return str(self.spectral_subclass)

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"{self.__class__.__name__}('{self!s}')"

    def __str__(self) -> str:
        """Return str(self)."""
        spectype = (f"{self.spectral_class}{self._subcls_str}"
                    f"{self.luminosity_class or ''}")
        return spectype

    def _tuple_factory(self) -> tuple[int, float]:
        spec_cls = self._cls_order.index(self.spectral_class)
        # if None, assume middle of spectral class
        if self.spectral_subclass is not None:
            sub_cls = self.spectral_subclass
        else:
            sub_cls = 5
        return (spec_cls, sub_cls)

    def __lt__(self, other) -> bool:
        """Return self < other."""
        if not isinstance(other, self.__class__):
            raise TypeError("Can only compare equal types.")
        return self._tuple_factory() < other._tuple_factory()

    def __le__(self, other) -> bool:
        """Return self < other."""
        if not isinstance(other, self.__class__):
            raise TypeError("Can only compare equal types.")
        return self._tuple_factory() <= other._tuple_factory()
