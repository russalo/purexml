"""libexpat version-awareness API (v0.1.2) — purexml's value-add over defusedxml.

Opt-in and non-enforcing: exposing it must not change parse behavior at import.
"""
import pytest

import purexml


def test_expat_version_exposed():
    v = purexml.EXPAT_VERSION
    assert isinstance(v, tuple) and len(v) == 3 and all(isinstance(n, int) for n in v)


def test_floors_are_documented_constants():
    assert purexml.SAFE_EXPAT_VERSION == (2, 6, 0)
    assert purexml.RECOMMENDED_EXPAT_VERSION == (2, 7, 2)


def test_expat_is_secure_on_this_runtime():
    # CI matrix (3.10–3.13) bundles libexpat >= the safe floor.
    assert purexml.expat_is_secure() is True


def test_assert_expat_secure_passes_here():
    purexml.assert_expat_secure()  # must not raise on a supported runtime


def test_assert_expat_secure_raises_below_floor():
    with pytest.raises(RuntimeError):
        purexml.assert_expat_secure(minimum=(99, 0, 0))


def test_expat_is_secure_custom_minimum():
    assert purexml.expat_is_secure(minimum=(0, 0, 0)) is True
    assert purexml.expat_is_secure(minimum=(99, 0, 0)) is False
