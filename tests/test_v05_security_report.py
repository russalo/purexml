"""v0.5 trust surface — `purexml.security_report()` (the posture API).

Read-only introspection: must accurately reflect THIS runtime, be deterministic,
frozen, printable, and have zero effect on parse behavior. The version-gated
mitigation mapping is tested both as-observed (against the real pyexpat version)
and by monkeypatching the runtime version below/at the floors.
"""
import xml.parsers.expat as _expat

import pytest

import purexml
from purexml import _expat_security as S


def test_exports_present():
    for name in ("security_report", "SecurityReport",
                 "BLOCKED", "EXPAT_MITIGATED", "OPT_IN", "LIVE"):
        assert hasattr(purexml, name), name


def test_status_constants_distinct_strings():
    vals = [purexml.BLOCKED, purexml.EXPAT_MITIGATED, purexml.OPT_IN, purexml.LIVE]
    assert all(isinstance(v, str) for v in vals)
    assert len(set(vals)) == 4


def test_report_is_frozen_printable_value():
    r = purexml.security_report()
    assert isinstance(r, purexml.SecurityReport)
    assert isinstance(r, tuple)  # namedtuple → frozen
    with pytest.raises(AttributeError):
        r.notes = ()
    # mitigations is a read-only mapping (MappingProxyType) — genuinely immutable,
    # not just a slot you can't rebind. A trust surface must not be mutable in place.
    with pytest.raises(TypeError):
        r.mitigations["billion_laughs"] = purexml.LIVE
    assert isinstance(str(r), str) and "security posture" in str(r)
    # the printable form surfaces the version and every mitigation status
    rendered = str(r)
    assert ".".join(map(str, r.expat_version)) in rendered
    for cls in r.mitigations:
        assert cls in rendered


def test_report_matches_runtime_expat():
    r = purexml.security_report()
    assert r.expat_version == _expat.version_info == purexml.EXPAT_VERSION
    assert r.expat_meets_safe_floor == (
        r.expat_version >= purexml.SAFE_EXPAT_VERSION)
    assert r.expat_meets_recommended == (
        r.expat_version >= purexml.RECOMMENDED_EXPAT_VERSION)
    assert r.recommended_limits is purexml.RECOMMENDED_LIMITS


def test_deterministic_and_read_only():
    # Same runtime → identical report; calling it does not change parse behavior.
    before = purexml.fromstring("<r><a>x</a></r>").tag
    assert purexml.security_report() == purexml.security_report()
    after = purexml.fromstring("<r><a>x</a></r>").tag
    assert before == after == "r"


def test_default_on_classes_always_blocked():
    # These are purexml's own handlers — version-independent, never LIVE/OPT_IN.
    m = purexml.security_report().mitigations
    for cls in ("billion_laughs", "quadratic_blowup",
                "external_entity_xxe", "external_dtd_retrieval"):
        assert m[cls] == purexml.BLOCKED


def test_structural_class_is_opt_in():
    assert (purexml.security_report().mitigations["structural_dos_depth_attrs_size"]
            == purexml.OPT_IN)


# -- version-gating: the report must change correctly with the expat version ----
# security_report() reads the module-level EXPAT_VERSION, so monkeypatching it
# exercises the below-floor / at-floor branches without a different interpreter.

@pytest.mark.parametrize("ver,large,memory,safe,rec", [
    ((2, 5, 0), purexml.LIVE,            purexml.LIVE,            False, False),  # pre-2.6
    ((2, 6, 0), purexml.EXPAT_MITIGATED, purexml.LIVE,            True,  False),  # safe floor
    ((2, 6, 1), purexml.EXPAT_MITIGATED, purexml.LIVE,            True,  False),  # between
    ((2, 7, 2), purexml.EXPAT_MITIGATED, purexml.EXPAT_MITIGATED, True,  True),   # recommended
    ((2, 9, 0), purexml.EXPAT_MITIGATED, purexml.EXPAT_MITIGATED, True,  True),   # above
])
def test_version_gating(monkeypatch, ver, large, memory, safe, rec):
    monkeypatch.setattr(S, "EXPAT_VERSION", ver)
    r = purexml.security_report()
    assert r.expat_version == ver
    assert r.expat_meets_safe_floor is safe
    assert r.expat_meets_recommended is rec
    assert r.mitigations["large_tokens_cve_2023_52425"] == large
    assert r.mitigations["disproportionate_memory"] == memory
    # purexml's own handlers are version-independent — a regression that
    # accidentally version-gated a BLOCKED class must be caught below the floor too.
    for cls in ("billion_laughs", "quadratic_blowup",
                "external_entity_xxe", "external_dtd_retrieval"):
        assert r.mitigations[cls] == purexml.BLOCKED
    assert r.mitigations["structural_dos_depth_attrs_size"] == purexml.OPT_IN


def test_below_recommended_emits_advisory_note(monkeypatch):
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 5, 0))
    notes = purexml.security_report().notes
    assert isinstance(notes, tuple)
    joined = " ".join(notes)
    assert "below the recommended floor" in joined
    # the LIVE classes are named so an adopter knows what is exposed
    assert "disproportionate_memory" in joined
    assert "large_tokens_cve_2023_52425" in joined


def test_at_recommended_no_floor_advisory(monkeypatch):
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 7, 2))
    notes = purexml.security_report().notes
    assert not any("below the recommended floor" in n for n in notes)
    # the structural opt-in advisory is always present (it's never auto-covered)
    assert any("opt-in" in n for n in notes)
