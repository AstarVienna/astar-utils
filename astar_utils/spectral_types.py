# -*- coding: utf-8 -*-
"""."""

import re
from dataclasses import dataclass, field

regex = re.compile(r"^(?P<spec_cls>[OBAFGKM])(?P<sub_cls>\d(?:\.\d)?)?"
                   "(?P<lum_cls> I{0,3}|IV|V)?$", re.A | re.I)


@dataclass
class SpectralType:
    """TBA."""

    spectral_class: str = field(init=False, repr=False, default=None)
    spectral_subclass: str = field(init=False, repr=False, default=None)
    luminosity_class: str = field(init=False, repr=False, default=None)
    spectype: str

    def __post_init__(self) -> None:
        """Validate input and populate fields."""
        if not (match := regex.fullmatch(self.spectype)):
            raise ValueError(self.spectype)

        classes = match.groupdict()
        self.spectral_class = classes["spec_cls"]
        self.spectral_subclass = classes["sub_cls"]
        self.luminosity_class = classes["lum_cls"]
