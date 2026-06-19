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
                 "BLOCKED", "EXPAT_MITIGATED", "EXPAT_PARTIAL", "OPT_IN", "LIVE"):
        assert hasattr(purexml, name), name


def test_status_constants_distinct_strings():
    vals = [purexml.BLOCKED, purexml.EXPAT_MITIGATED, purexml.EXPAT_PARTIAL,
            purexml.OPT_IN, purexml.LIVE]
    assert all(isinstance(v, str) for v in vals)
    assert len(set(vals)) == 5


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


def test_immutable_on_all_construction_paths():
    # PR#8 Codex P2: immutability must hold for direct construction and _replace(),
    # not only for security_report()'s output — __new__/_make normalize the inputs.
    r = purexml.security_report()
    # _replace with mutable inputs still yields a read-only mapping + tuple
    r2 = r._replace(mitigations={"x": purexml.LIVE}, notes=["n"])
    assert type(r2.mitigations).__name__ == "mappingproxy"
    assert isinstance(r2.notes, tuple)
    with pytest.raises(TypeError):
        r2.mitigations["x"] = purexml.BLOCKED
    # direct construction normalizes too (and a None recommended_limits prints)
    d = purexml.SecurityReport((2, 6, 1), True, False, None, {"k": "v"}, ["note"])
    assert type(d.mitigations).__name__ == "mappingproxy"
    with pytest.raises(TypeError):
        d.mitigations["k"] = "z"
    assert "None" in str(d)  # recommended_limits=None must not crash __str__


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

# Each expat-layer class gates on its OWN fix version, decoupled from the moving
# recommended-latest floor (2.8.1): large=2.6.0, memory=2.7.2, content=2.7.4 (v0.6),
# hash_flooding=2.8.0 (v0.9), attr_collision=2.8.1 (v0.6). So a version can report a
# class mitigated while still sitting below the recommended-latest floor.
_M = purexml.EXPAT_MITIGATED
_P = purexml.EXPAT_PARTIAL
_L = purexml.LIVE


# hash_flooding (hashf) is PARTIAL at EVERY version: never LIVE (hash-flood protection is
# present on all supported expat) and never a version-only MITIGATED (full 16-byte-salt
# hardening also needs CPython's pyexpat fix for CVE-2026-7210, which purexml can't verify
# at runtime — so it is reported conservatively as PARTIAL; v0.9 + PR#27 Codex).
@pytest.mark.parametrize("ver,large,memory,content,hashf,attr,safe,rec", [
    ((2, 5, 0), _L, _L, _L, _P, _L, False, False),  # pre-2.6
    ((2, 6, 0), _M, _L, _L, _P, _L, True,  False),  # safe floor (large fixed)
    ((2, 6, 1), _M, _L, _L, _P, _L, True,  False),  # between
    ((2, 7, 2), _M, _M, _L, _P, _L, True,  False),  # memory fixed
    ((2, 7, 4), _M, _M, _M, _P, _L, True,  False),  # content fixed (v0.6)
    ((2, 8, 0), _M, _M, _M, _P, _L, True,  False),  # expat has 16-byte API; wrapper unverifiable -> still PARTIAL
    ((2, 8, 1), _M, _M, _M, _P, _M, True,  True),   # attr fixed = recommended-latest
    ((2, 9, 0), _M, _M, _M, _P, _M, True,  True),   # above
])
def test_version_gating(monkeypatch, ver, large, memory, content, hashf, attr, safe, rec):
    monkeypatch.setattr(S, "EXPAT_VERSION", ver)
    r = purexml.security_report()
    assert r.expat_version == ver
    assert r.expat_meets_safe_floor is safe
    assert r.expat_meets_recommended is rec
    assert r.mitigations["large_tokens_cve_2023_52425"] == large
    assert r.mitigations["disproportionate_memory"] == memory
    assert r.mitigations["content_token_overflow_cve_2026_25210"] == content
    assert r.mitigations["hash_flooding_cve_2026_41080"] == hashf
    assert r.mitigations["attribute_collision_dos_cve_2026_45186"] == attr
    # hash_flooding is a HARDENING class — present on every supported expat, so it must
    # NEVER report LIVE (that would overstate; v0.9 design): PARTIAL below 2.8.0, else MITIGATED.
    assert r.mitigations["hash_flooding_cve_2026_41080"] != purexml.LIVE
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
    # the recommended-latest gap is ALWAYS surfaced (PR#10 Codex) ...
    assert "recommended-latest floor" in joined
    # ... AND the mapped LIVE classes are named so an adopter knows what's exposed
    assert "disproportionate_memory" in joined
    assert "large_tokens_cve_2023_52425" in joined


def test_at_recommended_no_floor_advisory(monkeypatch):
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 8, 1))  # the recommended-latest floor
    notes = purexml.security_report().notes
    assert not any("recommended" in n and "floor" in n for n in notes)
    # the structural opt-in advisory is always present (it's never auto-covered)
    assert any("opt-in" in n for n in notes)


def test_floor_advisory_no_longer_claims_untracked_gap(monkeypatch):
    # v0.9: every expat fix REACHABLE through purexml's paths is now individually tracked
    # (CVE-2026-41080 became the mapped hash_flooding PARTIAL class), so the generic floor
    # advisory must NOT claim an "untracked"/"not individually tracked" gap — that would be
    # false. It still fires below recommended-latest and names the LIVE tracked classes.
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 7, 4))
    r = purexml.security_report()
    assert r.expat_meets_recommended is False
    joined = " ".join(r.notes)
    assert "recommended-latest floor" in joined
    assert "not individually tracked" not in joined
    assert "untracked" not in joined
    # the still-live tracked class is named so a runtime below the floor never under-reports
    assert "attribute_collision_dos_cve_2026_45186" in joined


def test_hash_flooding_always_partial_two_layer(monkeypatch):
    # The v0.9 hardening-not-hole class, refined per PR#27 Codex (CVE-2026-7210): full
    # 16-byte-salt mitigation needs BOTH expat>=2.8.0 AND CPython's pyexpat fix, and purexml
    # can't verify the wrapper at runtime — so it reports PARTIAL on EVERY runtime (never
    # LIVE, never a version-only MITIGATED). The note is tailored by expat version.
    # Below the expat fix: salt-entropy nuance + CVE-2026-41080.
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 7, 4))
    r = purexml.security_report()
    assert r.mitigations["hash_flooding_cve_2026_41080"] == purexml.EXPAT_PARTIAL
    joined = " ".join(r.notes)
    assert "CVE-2026-41080" in joined and "salt" in joined

    # At/above the expat fix: still PARTIAL (NOT mitigated on expat alone), and the note must
    # surface the pyexpat wrapper requirement (CVE-2026-7210) that purexml can't verify.
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 8, 1))
    r2 = purexml.security_report()
    assert r2.mitigations["hash_flooding_cve_2026_41080"] == purexml.EXPAT_PARTIAL
    assert r2.mitigations["hash_flooding_cve_2026_41080"] != purexml.EXPAT_MITIGATED
    joined2 = " ".join(r2.notes)
    assert "CVE-2026-7210" in joined2


def test_attribute_collision_live_surfaces_max_attributes_lever(monkeypatch):
    # When the attr-collision class is live (<2.8.1), the report must point at the
    # opt-in max_attributes lever that bounds it (v0.6 design Q2).
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 7, 4))
    r = purexml.security_report()
    assert r.mitigations["attribute_collision_dos_cve_2026_45186"] == purexml.LIVE
    assert any("max_attributes" in n and "attribute_collision" in n for n in r.notes)
    # at/above the fix, that lever note is gone
    monkeypatch.setattr(S, "EXPAT_VERSION", (2, 8, 1))
    assert not any("attribute_collision_dos is live" in n
                   for n in purexml.security_report().notes)
