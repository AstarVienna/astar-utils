# -*- coding: utf-8 -*-
"""Contains SpectralType class."""

import re
from typing import ClassVar
from dataclasses import dataclass, field, InitVar


@dataclass(frozen=True, slots=True)
class SpectralType:
    r"""Parse and store stellar spectral types.

    This dataclass can understand a string constructor containing a valid
    stellar spectral type including "OBAFGKM"-spectral class, 0-9 subclass
    (including floats up to one decimal place) and luminosity class (roman
    numerals I-V), which are converted to attributes. The initial spectral
    type must match the regex "^[OBAFGKM](\d(\.\d)?)?(I{1,3}|IV|V)?$". Only the
    main spectral class ("OBAFGKM") is mandatory, both numerical subclass and
    luminosity class may be empty (None). Spectral subclasses (0.0-9.9) are
    internally stored as floats, meaning an initial type of e.g. "A0V" is
    considered identical to "A0.0V". Representations of an instance (``str``
    and ``repr``) always show integers whenever possible, regardless of the
    initially passed value.

    Instances of this class are always "frozen", meaning they cannot be changed
    after initial creation. It is not possible to manually assign the three
    individual attribute, creation can only happen via the constructor string
    described above.

    One of the main features of this class (and indeed motivation for its
    creation in the first place) is the ability to compare, and thus order,
    instances of the class based on their two-component spectral (sub)class.
    In this context, a "later" spectral type is considered "greater" than an
    "earlier" one, i.e. O < B < A < F < G < K < M, which is consistent with the
    convention of numerical subtypes, where 0 < 9 holds true. This is, however,
    in contrast to the physical meaning of this parameter, which is correlated
    with stellar effective temperature in reverse order, meaning T(A) > T(G)
    and T(F0) > T(F9), by convention. On the other hand, in many visualisations
    such as the Herzsprung-Russel diagram, it is common practice to represent
    temperature on the x-axis in descending order, meaning a sorted list of
    instances of this class will already have the typical order of such
    diagrams.

    In this context, the luminosity class (if any) is ignored for sorting and
    comparison (<, >, <=, >=), as it represents a second physical dimension.
    However, instances of this class may also be compared for equality (== and
    !=), in which case all three attributes are considered.

    Attributes
    ----------
    spectral_class : str
        Main spectral class (OBAFGKM).
    spectral_subclass : str or None
        Numerical spectral subclass (0.0-9.9).
    luminosity_class : str or None
        Roman numeral luminosity class (I-V).

    Examples
    --------
    >>> from astar_utils import SpectralType
    >>> spt = SpectralType("A0V")
    >>> spt.spectral_class
    'A'

    >>> spt.spectral_subclass
    0.0

    >>> spt.luminosity_class
    'V'

    >>> spts = [SpectralType(s) for s in
    ...         ["G2", "M4.0", "B3", "F8", "K6.5",
    ...          "A", "A0", "A9", "O8"]]
    >>> sorted(spts)  # doctest: +NORMALIZE_WHITESPACE
    [SpectralType('O8'),
     SpectralType('B3'),
     SpectralType('A0'),
     SpectralType('A'),
     SpectralType('A9'),
     SpectralType('F8'),
     SpectralType('G2'),
     SpectralType('K6.5'),
     SpectralType('M4')]

    Note that a missing spectral subtype is considered as 5 (middle of the
    main spectral class) in the context of sorting, as shown in the example
    with the spectral type "A" ending up between "A0" and "A9".
    """

    spectral_class: str = field(init=False, default="")
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

    @property
    def _comp_tuple(self) -> tuple[int, float]:
        # if None, assume middle of spectral class
        if self.spectral_subclass is not None:
            sub_cls = self.spectral_subclass
        else:
            sub_cls = 5
        return (self._cls_order.index(self.spectral_class), sub_cls)

    def __lt__(self, other) -> bool:
        """Return self < other."""
        if not isinstance(other, self.__class__):
            raise TypeError("Can only compare equal types.")
        return self._comp_tuple < other._comp_tuple

    def __le__(self, other) -> bool:
        """Return self < other."""
        if not isinstance(other, self.__class__):
            raise TypeError("Can only compare equal types.")
        return self._comp_tuple <= other._comp_tuple
