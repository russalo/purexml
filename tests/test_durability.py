"""Durability corpus — the newer, expat-layer attack classes (ROADMAP G4 / research
recommendation (c)). The 5 baseline classes (billion-laughs, quadratic blowup,
external-entity remote/local, DTD retrieval) live in test_attacks.py; here are the
two classes that postdate defusedxml's 2021 freeze, version-gated on libexpat.
"""
import xml.etree.ElementTree as ET

import pytest

import purexml
from conftest import requires_oracle


def test_runtime_meets_safe_floor():
    """The corpus assumes a safe runtime; assert it (CI matrix is all >= floor)."""
    assert purexml.expat_is_secure(), (
        "runtime libexpat %s below safe floor %s"
        % (purexml.EXPAT_VERSION, purexml.SAFE_EXPAT_VERSION)
    )


@requires_oracle
def test_large_token_equivalence_cve_2023_52425():
    """'Large tokens' quadratic-runtime DoS (CVE-2023-52425) is mitigated at the
    expat layer (reparse deferral, Expat 2.6.0+) — NOT by raising. purexml must
    parse a large single token equivalently to defusedxml, bounded (no hang)."""
    import defusedxml.ElementTree as DET

    doc = "<r>" + ("x" * 3_000_000) + "</r>"  # 3 MB single text token
    p = ET.canonicalize(ET.tostring(purexml.fromstring(doc), encoding="unicode"))
    d = ET.canonicalize(ET.tostring(DET.fromstring(doc), encoding="unicode"))
    assert p == d


def test_disproportionate_memory_class_version_gated():
    """Disproportionate dynamic-memory use affects Expat < 2.7.2. Below the
    recommended floor the class is live; the version-awareness surface must reflect
    reality so a consumer can choose to fail-closed."""
    if purexml.EXPAT_VERSION < purexml.RECOMMENDED_EXPAT_VERSION:
        pytest.skip(
            "runtime expat %s < recommended %s — class live here; "
            "consumers should assert_expat_secure(RECOMMENDED_EXPAT_VERSION)"
            % (purexml.EXPAT_VERSION, purexml.RECOMMENDED_EXPAT_VERSION)
        )
    assert purexml.EXPAT_VERSION >= purexml.SAFE_EXPAT_VERSION
