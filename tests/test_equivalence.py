"""Acceptance bar §4.1 — same-parse equivalence vs the defusedxml oracle, C14N.

For every ALLOW-path document, purexml's element tree MUST be identical to
defusedxml's, compared by canonicalization (kills attrib-order / tail-text /
namespace-prefix ambiguity). 0 disagreements.
"""
import xml.etree.ElementTree as ET

import pytest

import purexml
from conftest import ALLOW_CASES, requires_oracle


def _c14n(elem):
    return ET.canonicalize(ET.tostring(elem, encoding="unicode"))


@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_allow_parses(name):
    """Every allow-path doc parses to an Element (no over-blocking)."""
    elem = purexml.fromstring(ALLOW_CASES[name])
    assert elem is not None


@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_c14n_equivalent_to_oracle_str(name):
    import defusedxml.ElementTree as DET

    text = ALLOW_CASES[name]
    assert _c14n(purexml.fromstring(text)) == _c14n(DET.fromstring(text))


@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_c14n_equivalent_to_oracle_bytes(name):
    """file-observer passes raw bytes for docProps/app.xml — bytes input must be
    equivalent too (and an in-prolog encoding declaration is honored on bytes)."""
    import defusedxml.ElementTree as DET

    raw = ALLOW_CASES[name].encode("utf-8")
    assert _c14n(purexml.fromstring(raw)) == _c14n(DET.fromstring(raw))


def test_bytes_with_encoding_declaration():
    """app.xml-style: bytes carrying an encoding declaration parse (not the C
    parser's str-only ValueError)."""
    raw = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><r>x</r>'.encode("utf-8")
    assert purexml.fromstring(raw).text == "x"


def test_consumer_surface_exact():
    """The exact surface file-observer depends on (scanner answer #4): .iter with a
    Clark-notation tag, .get, .text, .tag, and direct child iteration. No .find/
    .findall/.attrib/.tail/.tostring/.getroot."""
    xml = ("<wb xmlns='urn:s'><sheets>"
           "<sheet name='S1'>  hi  </sheet><sheet name='S2'/>"
           "</sheets></wb>")
    root = purexml.fromstring(xml)
    assert root.tag == "{urn:s}wb"                                  # .tag (Clark)
    sheets = list(root.iter("{urn:s}sheet"))                        # .iter(Clark-tag)
    assert [s.get("name") for s in sheets] == ["S1", "S2"]          # .get
    assert sheets[0].text.strip() == "hi"                           # .text + strip
    child_tags = {c.tag for c in root}                              # child iteration
    assert child_tags == {"{urn:s}sheets"}


def test_determinism_repeated_parses_identical():
    text = ALLOW_CASES["namespaced"]
    first = _c14n(purexml.fromstring(text))
    for _ in range(5):
        assert _c14n(purexml.fromstring(text)) == first
