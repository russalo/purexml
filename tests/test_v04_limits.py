"""v0.4 acceptance — opt-in structural-DoS limits (mirror-plus).

Default OFF (strict mirror preserved); caps fire at the threshold; enforced under
streaming; RECOMMENDED_LIMITS has no false positives on real-shaped docs.
"""
import io

import pytest

import purexml
from purexml import (
    AttributesExceeded,
    DepthExceeded,
    Limits,
    LimitExceeded,
    RECOMMENDED_LIMITS,
    SizeExceeded,
)
from conftest import ALLOW_CASES, requires_oracle


# ---- default OFF == strict mirror ----
@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_default_off_equals_oracle(name):
    """No limits (default) must stay byte-identical to defusedxml."""
    import xml.etree.ElementTree as ET
    import defusedxml.ElementTree as DET

    text = ALLOW_CASES[name]
    a = ET.canonicalize(ET.tostring(purexml.fromstring(text), encoding="unicode"))
    b = ET.canonicalize(ET.tostring(DET.fromstring(text), encoding="unicode"))
    assert a == b
    # limits=None must be identical to omitting the arg
    c = ET.canonicalize(ET.tostring(purexml.fromstring(text, limits=None), encoding="unicode"))
    assert c == a


def test_unguarded_structural_dos_parses_by_default():
    # the documented gap: deep/floods parse with no limits (mirror of defusedxml)
    assert purexml.fromstring("<a>" * 5000 + "</a>" * 5000).tag == "a"
    assert purexml.fromstring("<r " + " ".join(f'a{i}="x"' for i in range(5000)) + "/>").tag == "r"


# ---- caps fire at the threshold; one below parses ----
def test_max_depth():
    doc = "<a>" * 50 + "</a>" * 50
    with pytest.raises(DepthExceeded):
        purexml.fromstring(doc, limits=Limits(max_depth=10))
    # exactly at limit ok; one over raises
    assert purexml.fromstring("<a>" * 10 + "</a>" * 10, limits=Limits(max_depth=10)).tag == "a"
    with pytest.raises(DepthExceeded):
        purexml.fromstring("<a>" * 11 + "</a>" * 11, limits=Limits(max_depth=10))


def test_max_attributes():
    flood = "<r " + " ".join(f'a{i}="x"' for i in range(20)) + "/>"
    with pytest.raises(AttributesExceeded):
        purexml.fromstring(flood, limits=Limits(max_attributes=5))
    ok = "<r " + " ".join(f'a{i}="x"' for i in range(5)) + "/>"
    assert purexml.fromstring(ok, limits=Limits(max_attributes=5)).tag == "r"


def test_max_bytes():
    with pytest.raises(SizeExceeded):
        purexml.fromstring("<r>" + "x" * 1000 + "</r>", limits=Limits(max_bytes=50))
    assert purexml.fromstring("<r>x</r>", limits=Limits(max_bytes=50)).tag == "r"


# ---- enforced across every entry point + under streaming ----
def test_limits_on_parse_and_fromstringlist(tmp_path):
    p = tmp_path / "d.xml"
    p.write_text("<a>" * 50 + "</a>" * 50)
    with pytest.raises(DepthExceeded):
        purexml.parse(str(p), limits=Limits(max_depth=10))
    with pytest.raises(DepthExceeded):
        purexml.fromstringlist(["<a>" * 50, "</a>" * 50], limits=Limits(max_depth=10))


def test_limits_under_iterparse_streaming():
    with pytest.raises(DepthExceeded):
        list(purexml.iterparse(io.StringIO("<a>" * 50 + "</a>" * 50),
                               limits=Limits(max_depth=10)))


def test_limits_via_xmlparser():
    with pytest.raises(DepthExceeded):
        purexml.parse(io.StringIO("<a>" * 50 + "</a>" * 50),
                      parser=purexml.XMLParser(limits=Limits(max_depth=10)))


# ---- RECOMMENDED_LIMITS: no false positives, catches pathology ----
def test_recommended_limits_no_false_positives():
    for text in ALLOW_CASES.values():
        purexml.fromstring(text, limits=RECOMMENDED_LIMITS)  # must not raise
    # a realistically large/deep-but-legal doc also passes
    big = "<r>" + "".join(f"<n d='{i}'>{i}</n>" for i in range(2000)) + "</r>"
    assert purexml.fromstring(big, limits=RECOMMENDED_LIMITS).tag == "r"


def test_recommended_limits_catches_pathology():
    with pytest.raises(DepthExceeded):
        purexml.fromstring("<a>" * 20000 + "</a>" * 20000, limits=RECOMMENDED_LIMITS)
    with pytest.raises(AttributesExceeded):
        purexml.fromstring("<r " + " ".join(f'a{i}="x"' for i in range(100000)) + "/>",
                           limits=RECOMMENDED_LIMITS)


# ---- exception hierarchy ----
def test_limit_exceptions_are_purexml_value_errors():
    for exc in (LimitExceeded, DepthExceeded, AttributesExceeded, SizeExceeded):
        assert issubclass(exc, purexml.PureXMLError)
        assert issubclass(exc, ValueError)
    assert issubclass(DepthExceeded, LimitExceeded)


def test_limits_namedtuple_defaults_to_none():
    assert Limits() == (None, None, None)
    assert Limits(max_depth=5).max_attributes is None
