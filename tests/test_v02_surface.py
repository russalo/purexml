"""v0.2 acceptance — the non-streaming ElementTree surface + the forbid_* knobs.

Equivalence to defusedxml.ElementTree for parse / XMLParser, the full 8-combo knob
matrix, DTDForbidden, plus the stdlib-parity fromstringlist and the namespace mirror.
"""
import io
import itertools
import xml.etree.ElementTree as ET

import pytest

import purexml
import purexml.ElementTree as PET
from conftest import ALLOW_CASES, requires_oracle


def c14n(elem):
    return ET.canonicalize(ET.tostring(elem, encoding="unicode"))


# ---------- parse ----------
@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_parse_equivalent_to_oracle(name):
    import defusedxml.ElementTree as DET

    text = ALLOW_CASES[name]
    assert c14n(purexml.parse(io.StringIO(text)).getroot()) == \
        c14n(DET.parse(io.StringIO(text)).getroot())


def test_parse_returns_elementtree_from_filename(tmp_path):
    p = tmp_path / "doc.xml"
    p.write_text("<r><a>x</a><b k='v'/></r>")
    tree = purexml.parse(str(p))
    assert isinstance(tree, ET.ElementTree)
    assert tree.getroot().find("a").text == "x"


@requires_oracle
def test_parse_blocks_attacks(attack_cases):
    for text in attack_cases.values():
        with pytest.raises(purexml.PureXMLError):
            purexml.parse(io.StringIO(text))


# ---------- XMLParser (parser= path) ----------
def test_xmlparser_drives_parse():
    root = purexml.parse(io.StringIO("<r xmlns:n='urn:x'><n:c>1</n:c></r>"),
                         parser=purexml.XMLParser()).getroot()
    assert [e.tag for e in root.iter()] == ["r", "{urn:x}c"]


def test_xmlparser_honors_forbid_dtd():
    with pytest.raises(purexml.DTDForbidden):
        purexml.parse(io.StringIO("<!DOCTYPE r><r/>"),
                      parser=purexml.XMLParser(forbid_dtd=True))


# ---------- fromstringlist (stdlib-parity extra) ----------
def test_fromstringlist_equals_fromstring_of_join():
    frags = ["<r ", "xmlns:n='urn:x'>", "<a>x</a>", "<n:b/>", "</r>"]
    assert c14n(purexml.fromstringlist(frags)) == c14n(purexml.fromstring("".join(frags)))


def test_fromstringlist_blocks_attacks(attack_cases):
    for text in attack_cases.values():
        with pytest.raises(purexml.PureXMLError):
            purexml.fromstringlist([text])


# ---------- the forbid_* knob matrix vs the oracle ----------
_MATRIX_DOCS = {
    "benign": "<r><a>x</a></r>",
    "internal_dtd": "<!DOCTYPE r [ <!ELEMENT r (#PCDATA)> ]><r>ok</r>",
    "internal_entity": "<!DOCTYPE r [ <!ENTITY e 'v'> ]><r>&e;</r>",
    "external_entity": "<!DOCTYPE r [ <!ENTITY e SYSTEM 'file:///no-such'> ]><r>&e;</r>",
    "external_dtd": "<!DOCTYPE r SYSTEM 'http://127.0.0.1:1/x.dtd'><r/>",
}


@requires_oracle
def test_forbid_knob_matrix_equivalence():
    """All 8 forbid_dtd×forbid_entities×forbid_external combos must match defusedxml
    — including deliberately-unsafe combos (equivalence, not always-safest)."""
    import defusedxml.ElementTree as DET

    def outcome(fn, doc, fd, fe, fx):
        try:
            return ("parse", c14n(fn(doc, forbid_dtd=fd, forbid_entities=fe,
                                     forbid_external=fx)))
        except Exception:  # noqa: BLE001 — kind, not type
            return ("raise", None)

    for fd, fe, fx in itertools.product([False, True], repeat=3):
        for name, doc in _MATRIX_DOCS.items():
            p = outcome(purexml.fromstring, doc, fd, fe, fx)
            d = outcome(DET.fromstring, doc, fd, fe, fx)
            assert p[0] == d[0], (fd, fe, fx, name, p[0], d[0])
            if p[0] == "parse":
                assert p[1] == d[1], (fd, fe, fx, name)


def test_forbid_dtd_raises_dtdforbidden():
    with pytest.raises(purexml.DTDForbidden):
        purexml.fromstring("<!DOCTYPE r [ <!ELEMENT r ANY> ]><r/>", forbid_dtd=True)
    # default (forbid_dtd=False) allows an entity-free DTD
    assert purexml.fromstring("<!DOCTYPE r [ <!ELEMENT r ANY> ]><r/>").tag == "r"


def test_forbid_params_are_positional():
    # defusedxml's signature is positional-or-keyword; a true drop-in matches it.
    with pytest.raises(purexml.DTDForbidden):
        purexml.fromstring("<!DOCTYPE r><r/>", True)  # forbid_dtd passed positionally


# ---------- namespace mirror ----------
def test_namespace_mirrors_defusedxml_shape():
    for n in ("fromstring", "parse", "XML", "XMLParser", "XMLParse",
              "XMLTreeBuilder", "tostring", "ParseError"):
        assert hasattr(PET, n), n
    assert PET.XML is PET.fromstring
    assert PET.XMLParse is PET.XMLParser and PET.XMLTreeBuilder is PET.XMLParser
    # ParseError / tostring are the stdlib objects (faithful re-export)
    assert PET.ParseError is ET.ParseError
    assert PET.tostring is ET.tostring


def test_iterparse_absent_until_v03():
    # honest scope: unimplemented defusedxml names are absent -> AttributeError,
    # not a silent wrong-parse.
    assert not hasattr(PET, "iterparse")
    with pytest.raises(AttributeError):
        PET.iterparse  # noqa: B018


def test_element_not_reexported_faithful_to_defusedxml():
    # defusedxml.ElementTree does not export Element; neither do we.
    assert "Element" not in PET.__all__


def test_literal_sed_migration():
    # the s/defusedxml/purexml/ promise for the implemented surface
    from purexml.ElementTree import fromstring as xml_fromstring
    assert xml_fromstring("<r/>").tag == "r"


# ---------- PR#4 bot findings: regressions guarded ----------
@pytest.mark.parametrize("bad", ["<r></x>", "<r>", "<!DOCTYPE r [<!ENTITY e 'v'>]><r>&e;</r>"])
def test_heavy_state_released_on_error_paths(bad):
    """PR#4: malformed/blocked input must still break the expat-parser<->self cycle
    so the heavy parser + tree are freed promptly (the v0.2 feed/close split
    regressed the v0.1.2 fix on error paths). The lightweight XMLParser shell itself
    lingers in the exception traceback frame — universal Python behavior, not a leak
    — so we assert the heavy refs are cleared rather than weakref the shell."""
    from purexml._parser import XMLParser

    p = XMLParser()
    with pytest.raises(Exception):  # noqa: B017 — ParseError or PureXMLError
        p.feed(bad)
        p.close()
    assert p.parser is None and p.target is None, "heavy parser/tree not released on error"


def test_custom_target_without_comment_pi():
    """PR#4: a custom target providing only the core protocol must work — the
    comment/pi handlers are optional (guarded by hasattr, like the stdlib)."""
    from xml.etree.ElementTree import TreeBuilder

    class Minimal:
        def __init__(self):
            self._tb = TreeBuilder()

        def start(self, tag, attrs):
            return self._tb.start(tag, attrs)

        def end(self, tag):
            return self._tb.end(tag)

        def data(self, d):
            return self._tb.data(d)

        def close(self):
            return self._tb.close()

    p = purexml.XMLParser(target=Minimal())  # must not raise AttributeError
    p.feed("<r><!-- dropped --><a>x</a></r>")
    root = p.close()
    assert root.tag == "r" and root.find("a").text == "x"
