# -*- coding: utf-8 -*-
"""Unit tests for spectral_types.py."""

import pytest

from astar_utils import SpectralType


class TestParsesTypes:
    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize("spec_cls", [*"OBAFGKM"])
    def test_parses_valid_spec_cls(self, spec_cls):
        spt = SpectralType(spec_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass is None
        assert spt.luminosity_class is None

    @pytest.mark.xfail(reason="not yet implemented")
    def test_fails_on_invalid_spec_cls(self):
        with pytest.raises(ValueError):
            SpectralType("X")

    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize(("spec_cls", "sub_cls"),
                             [(*"A0",), (*"G2",), ("F", "3.5"), ("K", "7.5"),
                              (*"M2",), (*"B9",), ("G", "5.0"), ("F", "0.5")])
    def test_parses_valid_spec_and_sub_cls(self, spec_cls, sub_cls):
        spt = SpectralType(spec_cls + sub_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass == sub_cls
        assert spt.luminosity_class is None

    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize("spec_sub_cls", ["X2", "Y3.5", "G99", "K1.2222"])
    def test_fails_on_invalid_spec_and_sub_cls(self, spec_sub_cls):
        with pytest.raises(ValueError):
            SpectralType(spec_sub_cls)

    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize(("spec_cls", "lum_cls"),
                             [(*"AV",), (*"GI",), ("F", "III"), ("K", "IV")])
    def test_parses_valid_spec_and_lum_cls(self, spec_cls, lum_cls):
        spt = SpectralType(spec_cls + lum_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass is None
        assert spt.luminosity_class == lum_cls

    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize("spec_lum_cls", ["II", "YVII", "GIIV", "KIVI"])
    def test_fails_on_invalid_spec_and_lum_cls(self, spec_lum_cls):
        with pytest.raises(ValueError):
            SpectralType(spec_lum_cls)

    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize(("spec_cls", "sub_cls", "lum_cls"),
                             [(*"A0V",), (*"G2I",), ("F", "3.5", "II"),
                              ("K", "7.5", "IV"), (*"M2V",), (*"B9I",),
                              ("G", "5.0", "III"), ("F", "0.5", "V")])
    def test_parses_valid_spec_sub_lum_cls(self, spec_cls, sub_cls, lum_cls):
        spt = SpectralType(spec_cls + sub_cls + lum_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass == sub_cls
        assert spt.luminosity_class == lum_cls

    @pytest.mark.xfail(reason="not yet implemented")
    @pytest.mark.parametrize("spec_sub_lum_cls",
                             ["Bogus", "G3IIV", "K4.5IVI", "B999IV"])
    def test_fails_on_invalid_spec_sub_lum_cls(self, spec_sub_lum_cls):
        with pytest.raises(ValueError):
            SpectralType(spec_sub_lum_cls)
