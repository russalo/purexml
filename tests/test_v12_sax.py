"""v0.12 — `purexml.sax` (+ `purexml.expatreader`) drop-in.

Event-driven: a `ContentHandler` receives the callback stream from a hardened `XMLReader`.
The falsify-first rules carry over to the event surface: same parses produce the same event
stream (oracle-equal), same attacks blocked (a `PureXMLError`), malformed → stdlib
`SAXParseException`, no I/O on untrusted input. `parseString` is bytes-only (mirrors the oracle).
"""
import gc
import weakref
from io import BytesIO

import pytest
from xml.sax import SAXParseException
from xml.sax.handler import ContentHandler

import purexml
import purexml.sax as PS
from conftest import ALLOW_CASES, assert_no_io, requires_oracle


class _Rec(ContentHandler):
    """Records the callback stream as comparable tuples."""

    def __init__(self):
        self.ev = []

    def startElement(self, name, attrs):
        self.ev.append(("S", name, tuple(sorted(attrs.items()))))

    def endElement(self, name):
        self.ev.append(("E", name))

    def characters(self, content):
        self.ev.append(("C", content))

    def startPrefixMapping(self, prefix, uri):
        self.ev.append(("NS", prefix, uri))


def _events(mod, data):
    h = _Rec()
    mod.parseString(data, h)
    return h.ev


def test_parsestring_event_stream():
    assert _events(PS, b"<r><a>x</a></r>") == [
        ("S", "r", ()), ("S", "a", ()), ("C", "x"), ("E", "a"), ("E", "r")]


def test_make_parser_drives_a_handler_over_a_stream():
    parser = PS.make_parser()
    h = _Rec()
    parser.setContentHandler(h)
    parser.parse(BytesIO(b"<r><a>x</a></r>"))
    assert ("S", "r", ()) in h.ev and ("E", "r") in h.ev


def test_module_parse_over_stream():
    # the module-level parse(source, handler) (vs the reader's own .parse) over a byte stream
    h = _Rec()
    PS.parse(BytesIO(b"<r><a>x</a></r>"), h)
    assert h.ev == [("S", "r", ()), ("S", "a", ()), ("C", "x"), ("E", "a"), ("E", "r")]


def test_parsestring_errorhandler_none_defaults():
    # parseString accepts errorHandler=None (mirrors defusedxml) and substitutes a default.
    h = _Rec()
    PS.parseString(b"<r/>", h, errorHandler=None)
    assert ("S", "r", ()) in h.ev


@pytest.mark.parametrize("name", [
    "internal_general_entity", "internal_param_entity", "billion_laughs",
    "xxe_local_file", "xxe_network", "xxe_param_external_dtd",
])
def test_attacks_block_with_purexml_exception_no_io(name, attack_cases):
    src = attack_cases[name].encode()
    with assert_no_io():
        with pytest.raises(purexml.PureXMLError):
            _events(PS, src)


def test_external_dtd_blocked_no_fetch():
    # On the SAX path the external-DTD subset load reaches the external-ref handler, so with
    # forbid_external=True (default) it raises ExternalReferenceForbidden — and NO I/O occurs
    # (matches defusedxml.sax; verified by the trip-wire).
    doc = b'<?xml version="1.0"?><!DOCTYPE r SYSTEM "http://127.0.0.1:1/x.dtd"><r/>'
    with assert_no_io():
        with pytest.raises(purexml.ExternalReferenceForbidden):
            _events(PS, doc)


def test_unparsed_ndata_entity_blocked():
    ndata = (b'<?xml version="1.0"?><!DOCTYPE r [ <!NOTATION gif SYSTEM "g">'
             b'<!ENTITY pic SYSTEM "file:///etc/hostname" NDATA gif> ]><r/>')
    with assert_no_io():
        with pytest.raises(purexml.EntitiesForbidden):
            _events(PS, ndata)


def test_external_ref_backstop_when_entities_allowed():
    # forbid_entities=False allows the declaration; the external-ref handler is the backstop.
    ext = (b'<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/hostname"> ]>'
           b'<r>&x;</r>')
    h = _Rec()
    with assert_no_io():
        with pytest.raises(purexml.ExternalReferenceForbidden):
            PS.parseString(ext, h, forbid_entities=False)


def test_forbid_dtd_raises_dtdforbidden():
    doc = b'<?xml version="1.0"?><!DOCTYPE r [ <!ELEMENT r (#PCDATA)> ]><r>ok</r>'
    h = _Rec()
    PS.parseString(doc, h)  # default forbid_dtd=False: parses
    assert ("S", "r", ()) in h.ev
    with pytest.raises(purexml.DTDForbidden):
        PS.parseString(doc, _Rec(), forbid_dtd=True)


def test_malformed_raises_saxparseexception_not_block():
    # Malformed input is the stdlib SAXParseException via the ErrorHandler, NOT a PureXMLError.
    with pytest.raises(SAXParseException) as exc:
        PS.parseString(b"<r><a></r>", _Rec())
    assert not isinstance(exc.value, purexml.PureXMLError)


def test_parsestring_is_bytes_only_like_oracle():
    # Deliberate parity: defusedxml.sax.parseString is bytes-only (BytesIO(string)); a str raises
    # TypeError. purexml mirrors it — no over-accepting beyond the oracle (cf. minidom/PR#28).
    with pytest.raises(TypeError):
        PS.parseString("<r/>", _Rec())  # type: ignore[arg-type]


def test_sax_reader_no_leak_on_error():
    # purexml clears the reader->parser edge on every path (`parse()` override; the stdlib
    # ExpatParser clears _parser only on success). Unlike ElementTree/minidom the SAX reader is
    # NOT fully refcount-reclaimable — a residual cycle lives in pyexpat's exception retention
    # (defusedxml.sax has it too) — but it is collected by cyclic GC (NO LEAK), and the edge IS
    # cleared. This test pins both: the edge is gone, and gc.collect() reclaims the reader.
    from purexml.expatreader import _DefusedExpatParser

    gc.disable()
    try:
        for payload in (b"<r>",  # malformed
                        b'<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x "v"> ]><r>&x;</r>'):  # blocked
            p = _DefusedExpatParser()
            p.setContentHandler(_Rec())
            ref = weakref.ref(p)
            try:
                p.parse(BytesIO(payload))
            except Exception:  # noqa: BLE001
                pass
            assert p._parser is None, "reader->parser edge not cleared on the error path"
            del p
            gc.collect()
            assert ref() is None, "reader leaked — not even cyclic GC reclaimed it"
    finally:
        gc.enable()


# -- oracle-gated parity (the equivalence guarantee) --------------------------------

@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_sax_allow_event_parity_with_oracle(name):
    import defusedxml.sax as DS

    data = ALLOW_CASES[name].encode()
    oracle_ev = oracle_err = None
    try:
        oracle_ev = _events(DS, data)
    except Exception as e:  # noqa: BLE001
        oracle_err = e
    if oracle_err is not None:
        # both-raise is also parity, as long as purexml's refusal is a PureXMLError
        with pytest.raises(purexml.PureXMLError):
            _events(PS, data)
    else:
        assert _events(PS, data) == oracle_ev


@requires_oracle
@pytest.mark.parametrize("name", [
    "internal_general_entity", "internal_param_entity", "billion_laughs",
    "xxe_local_file", "xxe_network", "xxe_param_external_dtd",
])
def test_sax_block_parity_with_oracle(name, attack_cases):
    from defusedxml.common import DefusedXmlException
    import defusedxml.sax as DS

    data = attack_cases[name].encode()
    with pytest.raises(DefusedXmlException):
        _events(DS, data)
    with pytest.raises(purexml.PureXMLError):
        _events(PS, data)
