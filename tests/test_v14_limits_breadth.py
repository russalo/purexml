"""v0.14 — opt-in `Limits` extended to minidom + sax (mirror-plus defense-in-depth).

The v0.4 structural-DoS caps (max_depth / max_attributes / max_bytes) now reach the breadth
surfaces, opt-in and default-off. Falsify-first: default (`limits=None`) is byte-identical to
today (the differential-fuzz gate guards that); with a cap, the SAME exception types fire as on
the ElementTree path. xmlrpc is deliberately out (no `limits=` call site; gzip-bomb is its cap).
"""
from io import BytesIO

import pytest
from xml.sax.handler import ContentHandler

import purexml
import purexml.minidom as PM
import purexml.sax as PS
from purexml import AttributesExceeded, DepthExceeded, Limits, SizeExceeded

_DEEP = "<r>" + "<a>" * 50 + "</a>" * 50 + "</r>"
_FLOOD = "<r " + " ".join("a%d='1'" % i for i in range(20)) + "/>"


# -- minidom --------------------------------------------------------------------------

def test_minidom_default_no_caps_parses():
    # limits=None == strict mirror: a deep/flooded doc parses with no cap (default-off).
    assert PM.parseString(_DEEP).documentElement.tagName == "r"
    assert PM.parseString(_FLOOD).documentElement.tagName == "r"


def test_minidom_max_depth():
    with pytest.raises(DepthExceeded):
        PM.parseString(_DEEP, limits=Limits(max_depth=10))


def test_minidom_max_attributes():
    with pytest.raises(AttributesExceeded):
        PM.parseString(_FLOOD, limits=Limits(max_attributes=5))


def test_minidom_max_bytes():
    with pytest.raises(SizeExceeded):
        PM.parseString("<r>xxxxxxxx</r>", limits=Limits(max_bytes=4))


def test_minidom_under_limit_ok():
    doc = PM.parseString("<r><a k='v'>x</a></r>", limits=purexml.RECOMMENDED_LIMITS)
    assert doc.documentElement.tagName == "r"  # no false positive under generous caps


def test_minidom_parse_file_enforces_depth(tmp_path):
    p = tmp_path / "d.xml"
    p.write_text(_DEEP)
    with pytest.raises(DepthExceeded):
        PM.parse(str(p), limits=Limits(max_depth=10))


# -- sax ------------------------------------------------------------------------------

def test_sax_default_no_caps_parses():
    PS.parseString(_DEEP.encode(), ContentHandler())  # no raise (mirror)


def test_sax_max_depth():
    with pytest.raises(DepthExceeded):
        PS.parseString(_DEEP.encode(), ContentHandler(), limits=Limits(max_depth=10))


def test_sax_max_attributes():
    with pytest.raises(AttributesExceeded):
        PS.parseString(_FLOOD.encode(), ContentHandler(), limits=Limits(max_attributes=5))


def test_sax_max_bytes():
    with pytest.raises(SizeExceeded):
        PS.parseString(b"<r>xxxxxxxx</r>", ContentHandler(), limits=Limits(max_bytes=4))


def test_sax_parse_stream_enforces_depth():
    with pytest.raises(DepthExceeded):
        PS.parse(BytesIO(_DEEP.encode()), ContentHandler(), limits=Limits(max_depth=10))


def test_sax_depth_boundary_and_completion():
    # A doc whose max depth == the cap PARSES (enter+leave balance); one deeper raises. This
    # exercises the leave() path on a completing parse and pins the off-by-one.
    at_cap = ("<r>" + "<a>" * 4 + "</a>" * 4 + "</r>").encode()   # nesting depth 5
    PS.parseString(at_cap, ContentHandler(), limits=Limits(max_depth=5))  # exactly at cap: ok
    with pytest.raises(DepthExceeded):
        PS.parseString(at_cap, ContentHandler(), limits=Limits(max_depth=4))


def test_sax_namespace_aware_path_counts():
    # NS-on (namespaceHandling=1) drives start_element_ns/end_element_ns — the caps must
    # count there too. Built directly since make_parser defaults to NS-off.
    from purexml.expatreader import create_parser

    deep_ns = ("<r xmlns='urn:d'>" + "<a>" * 50 + "</a>" * 50 + "</r>").encode()
    over = create_parser(1, limits=Limits(max_depth=10))  # namespaceHandling=1
    over.setContentHandler(ContentHandler())
    with pytest.raises(DepthExceeded):
        over.parse(BytesIO(deep_ns))
    # and a NS parse UNDER the cap completes (exercises start_element_ns + end_element_ns leave)
    ok = create_parser(1, limits=Limits(max_depth=1000))
    ok.setContentHandler(ContentHandler())
    ok.parse(BytesIO(b"<r xmlns='urn:d'><a>x</a></r>"))


# -- equivalence preserved (default path) ---------------------------------------------

def test_default_limits_none_is_byte_identical():
    # limits=None must not perturb output — minidom toxml + sax events identical with/without
    # the param (the differential-fuzz gate covers this broadly; this is a focused guard).
    doc = "<r xmlns:n='urn:x'><n:c a='1'>hi</n:c><d>x</d></r>"
    assert PM.parseString(doc).toxml() == PM.parseString(doc, limits=None).toxml()

    class _Rec(ContentHandler):
        def __init__(self): self.ev = []
        def startElement(self, n, a): self.ev.append(("S", n))
        def endElement(self, n): self.ev.append(("E", n))
        def characters(self, c): self.ev.append(("C", c))
    h1, h2 = _Rec(), _Rec()
    PS.parseString(doc.encode(), h1)
    PS.parseString(doc.encode(), h2, limits=None)
    assert h1.ev == h2.ev


def test_xmlrpc_has_no_limits_param():
    # xmlrpc is deliberately OUT of scope (no limits= call site; gzip-bomb is its structural cap).
    import inspect
    assert "limits" not in inspect.signature(purexml.xmlrpc.monkey_patch).parameters
