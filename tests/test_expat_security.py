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
    # RECOMMENDED tracks latest-stable libexpat (bumped to 2.8.2 in v0.10.1 after the
    # 2026-06-25 integer-overflow/memory-safety release); it is >= the functional floor.
    assert purexml.RECOMMENDED_EXPAT_VERSION == (2, 8, 2)
    assert purexml.RECOMMENDED_EXPAT_VERSION >= purexml.SAFE_EXPAT_VERSION


def test_functional_floor_met_on_this_runtime():
    # CI matrix (3.10–3.13) bundles libexpat >= the functional floor (2.6.0).
    assert purexml.expat_is_secure(purexml.SAFE_EXPAT_VERSION) is True


def test_default_check_uses_conservative_floor():
    # PR#3 Codex: the default secure check is fail-safe (RECOMMENDED, not SAFE).
    assert purexml.expat_is_secure() == (
        purexml.EXPAT_VERSION >= purexml.RECOMMENDED_EXPAT_VERSION
    )


def test_assert_expat_secure_functional_floor_passes():
    purexml.assert_expat_secure(purexml.SAFE_EXPAT_VERSION)  # functional floor met on CI


def test_assert_expat_secure_raises_below_floor():
    with pytest.raises(RuntimeError):
        purexml.assert_expat_secure(minimum=(99, 0, 0))


def test_expat_is_secure_custom_minimum():
    assert purexml.expat_is_secure(minimum=(0, 0, 0)) is True
    assert purexml.expat_is_secure(minimum=(99, 0, 0)) is False


def test_version_argument_accepts_string():
    # PR#3 Gemini: a "x.y.z" string must work, not raise TypeError.
    assert purexml.expat_is_secure("2.6.0") == purexml.expat_is_secure((2, 6, 0))
    assert purexml.expat_is_secure("99.0.0") is False


def test_assert_expat_secure_string_message_well_formed():
    with pytest.raises(RuntimeError) as exc:
        purexml.assert_expat_secure("99.0.0")
    msg = str(exc.value)
    assert "99.0.0" in msg  # not malformed char-split "9...9...0"
    # PR#29 Codex: the message must NOT enumerate a fixed class list (it goes stale on every
    # floor bump and misnames the gap). It points at security_report() for the accurate posture.
    assert "security_report()" in msg
    assert "billion laughs" not in msg and "disproportionate" not in msg
