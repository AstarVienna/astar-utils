# -*- coding: utf-8 -*-
"""Unit tests for spectral_types.py."""

import pytest
import operator

from astar_utils import SpectralType


class TestParsesTypes:
    @pytest.mark.parametrize("spec_cls", [*"OBAFGKM"])
    def test_parses_valid_spec_cls(self, spec_cls):
        spt = SpectralType(spec_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass is None
        assert spt.luminosity_class is None

    def test_fails_on_invalid_spec_cls(self):
        with pytest.raises(ValueError):
            SpectralType("X")

    @pytest.mark.parametrize(("spec_cls", "sub_cls"),
                             [(*"A0",), (*"G2",), ("F", "3.5"), ("K", "7.5"),
                              (*"M2",), (*"B9",), ("G", "5.0"), ("F", "0.5")])
    def test_parses_valid_spec_and_sub_cls(self, spec_cls, sub_cls):
        spt = SpectralType(spec_cls + sub_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass == float(sub_cls)
        assert spt.luminosity_class is None

    @pytest.mark.parametrize("spec_sub_cls", ["X2", "Y3.5", "G99", "K1.2222"])
    def test_fails_on_invalid_spec_and_sub_cls(self, spec_sub_cls):
        with pytest.raises(ValueError):
            SpectralType(spec_sub_cls)

    @pytest.mark.parametrize(("spec_cls", "lum_cls"),
                             [(*"AV",), (*"GI",), ("F", "III"), ("K", "IV")])
    def test_parses_valid_spec_and_lum_cls(self, spec_cls, lum_cls):
        spt = SpectralType(spec_cls + lum_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass is None
        assert spt.luminosity_class == lum_cls

    @pytest.mark.parametrize("spec_lum_cls", ["II", "YVII", "GIIV", "KIVI"])
    def test_fails_on_invalid_spec_and_lum_cls(self, spec_lum_cls):
        with pytest.raises(ValueError):
            SpectralType(spec_lum_cls)

    @pytest.mark.parametrize(("spec_cls", "sub_cls", "lum_cls"),
                             [(*"A0V",), (*"G2I",), ("F", "3.5", "II"),
                              ("K", "7.5", "IV"), (*"M2V",), (*"B9I",),
                              ("G", "5.0", "III"), ("F", "0.5", "V")])
    def test_parses_valid_spec_sub_lum_cls(self, spec_cls, sub_cls, lum_cls):
        spt = SpectralType(spec_cls + sub_cls + lum_cls)
        assert spt.spectral_class == spec_cls
        assert spt.spectral_subclass == float(sub_cls)
        assert spt.luminosity_class == lum_cls

    @pytest.mark.parametrize("spec_sub_lum_cls",
                             ["Bogus", "G3IIV", "K4.5IVI", "B999IV"])
    def test_fails_on_invalid_spec_sub_lum_cls(self, spec_sub_lum_cls):
        with pytest.raises(ValueError):
            SpectralType(spec_sub_lum_cls)


class TestComparesTypes:
    @pytest.mark.parametrize(("ssl_cls_a", "ssl_cls_b"),
                             [("A0V", "A0V"), ("G2", "G2.0"),
                              ("M3III", "M3.0III")])
    def test_compares_classes_as_equal(self, ssl_cls_a, ssl_cls_b):
        spt_a = SpectralType(ssl_cls_a)
        spt_b = SpectralType(ssl_cls_b)
        assert spt_a == spt_b

    @pytest.mark.parametrize(("ssl_cls_a", "ssl_cls_b"),
                             [("A0V", "A1V"), ("G2", "G2.5"),
                              ("M3III", "M8.0III"), ("B3V", "BV")])
    def test_compares_order_within_spec_cls(self, ssl_cls_a, ssl_cls_b):
        spt_a = SpectralType(ssl_cls_a)
        spt_b = SpectralType(ssl_cls_b)
        assert spt_a < spt_b
        assert spt_b > spt_a

    @pytest.mark.parametrize(("ssl_cls_a", "ssl_cls_b"),
                             [("A0V", "G1V"), ("G", "M"), ("OII", "GIV"),
                              ("K3III", "M8.0III"), ("BV", "KI")])
    def test_compares_order_across_spec_cls(self, ssl_cls_a, ssl_cls_b):
        spt_a = SpectralType(ssl_cls_a)
        spt_b = SpectralType(ssl_cls_b)
        assert spt_a < spt_b
        assert spt_b > spt_a

    @pytest.mark.parametrize(("ssl_cls_a", "ssl_cls_b"),
                             [("A0V", "G1V"), ("G", "M"), ("OII", "GIV"),
                              ("K3III", "M8.0III"), ("BV", "KI"),
                              ("A0V", "A1V"), ("G2", "G2.5"),
                              ("M3III", "M8.0III"), ("B3V", "BV")])
    def test_compares_order_with_equal(self, ssl_cls_a, ssl_cls_b):
        spt_a = SpectralType(ssl_cls_a)
        spt_b = SpectralType(ssl_cls_b)
        assert spt_a <= spt_b
        assert spt_b >= spt_a

    @pytest.mark.parametrize("operation", [operator.gt, operator.lt,
                                           operator.ge, operator.le])
    def test_throws_on_invalid_compare(self, operation):
        with pytest.raises(TypeError):
            operation(SpectralType("A0V"), 42)


class TestRepresentations:
    @pytest.mark.parametrize(("ssl_cls", "exptcted"),
                             [("A0V", "SpectralType('A0V')"),
                              ("G2", "SpectralType('G2')"),
                              ("K9.0", "SpectralType('K9')"),
                              ("B2.5", "SpectralType('B2.5')"),
                              ("M3.0III", "SpectralType('M3III')"),
                              ("KII", "SpectralType('KII')"),])
    def test_repr(self, ssl_cls, exptcted):
        spt = SpectralType(ssl_cls)
        assert repr(spt) == exptcted

    @pytest.mark.parametrize(("ssl_cls", "exptcted"),
                             [("A0V", "A0V"),
                              ("G2", "G2"),
                              ("K9.0", "K9"),
                              ("B2.5", "B2.5"),
                              ("M3.0III", "M3III"),
                              ("KII", "KII"),])
    def test_str(self, ssl_cls, exptcted):
        spt = SpectralType(ssl_cls)
        assert str(spt) == exptcted

    @pytest.mark.parametrize(("ssl_cls", "exptcted"),
                             [("A0V", 20), ("G2", 42), ("K9.0", 59),
                              ("B2.7", 12.7), ("M3.1III", 63.1), ("KII", 50),])
    def test_num_spec_cls(self, ssl_cls, exptcted):
        spt = SpectralType(ssl_cls)
        assert spt.numerical_spectral_class == exptcted

    @pytest.mark.parametrize(("ssl_cls", "exptcted"),
                             [("A0V", 5), ("G2", 5), ("K9.0", 5), ("M4IV", 4),
                              ("B2II", 2), ("M3.1III", 3), ("KII", 2),])
    def test_num_lum_cls(self, ssl_cls, exptcted):
        spt = SpectralType(ssl_cls)
        assert spt.numerical_luminosity_class == exptcted


class TestUpperLowerCase:
    def test_uppers_lower_case(self):
        spt_a = SpectralType("A0V")
        spt_b = SpectralType("a0v")
        assert spt_a == spt_b

    @pytest.mark.parametrize("mixcase", ["m2.5III", "M2.5iii"])
    def test_uppers_lower_case_mixed(self, mixcase):
        spt_a = SpectralType("M2.5III")
        spt_b = SpectralType(mixcase)
        assert spt_a == spt_b
