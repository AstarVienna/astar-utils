# -*- coding: utf-8 -*-
"""."""

import re
from dataclasses import dataclass, field

regex = re.compile(r"^(?P<spec_cls>[OBAFGKM])(?P<sub_cls>\d(?:\.\d)?)?"
                   "(?P<lum_cls>I{1,3}|IV|V)?$", re.A | re.I)


@dataclass
class SpectralType:
    """TBA."""

    spectral_class: str | None = field(init=False, repr=False, default=None)
    spectral_subclass: float | None = field(init=False, repr=False, default=None)
    luminosity_class: str | None = field(init=False, repr=False, default=None)
    spectype: str

    def __post_init__(self) -> None:
        """Validate input and populate fields."""
        if not (match := regex.fullmatch(self.spectype)):
            raise ValueError(self.spectype)

        classes = match.groupdict()
        self.spectral_class = classes["spec_cls"]
        self.luminosity_class = classes["lum_cls"]

        if classes["sub_cls"] is not None:
            self.spectral_subclass = float(classes["sub_cls"])
