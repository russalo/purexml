"""v0.3 acceptance — hardened iterparse (the streaming slice).

Event-stream + raise-point equivalence to defusedxml.iterparse, no-fetch under
streaming, the forbid_* knob matrix, cleanup-on-error through the iterator, and the
now-complete namespace.
"""
import io
import itertools

import pytest

import purexml
from conftest import IOTouched, assert_no_io, requires_oracle

EVENT_MODES = [None, ("start",), ("end",), ("start", "end"),
               ("start", "end", "start-ns", "end-ns")]


def _stream(fn, text, events):
    """Sequence of (event, tag-or-payload) — the event-stream identity."""
    out = []
    for ev, el in fn(io.StringIO(text), events):
        out.append((ev, el.tag if hasattr(el, "tag") else el))
    return out


@requires_oracle
@pytest.mark.parametrize("events", EVENT_MODES)
def test_event_stream_equivalent_to_oracle(events):
    import defusedxml.ElementTree as DET

    docs = [
        "<root xmlns:n='urn:x'><n:a k='1'>x</n:a><b>y</b><c/></root>",
        "<r><a><b><c>deep</c></b></a><a2/></r>",
        "<?xml version='1.0'?><!-- c --><?pi go?><r>t</r>",
    ]
    for doc in docs:
        assert _stream(purexml.iterparse, doc, events) == _stream(DET.iterparse, doc, events)


def test_default_events_is_end_only():
    evs = [ev for ev, _ in purexml.iterparse(io.StringIO("<r><a/></r>"))]
    assert set(evs) == {"end"}


# ---- same raise-point under streaming ----
ATTACKS = {
    "internal_entity": "<!DOCTYPE r [<!ENTITY e 'v'>]><r>&e;</r>",
    "billion_laughs": "<!DOCTYPE l [<!ENTITY a 'x'><!ENTITY b '&a;&a;&a;'>]><l>&b;</l>",
    "xxe_local": "<!DOCTYPE r [<!ENTITY x SYSTEM 'file:///no-such'>]><r>&x;</r>",
    "xxe_net": "<!DOCTYPE r [<!ENTITY x SYSTEM 'http://127.0.0.1:1/a'>]><r>&x;</r>",
    "malformed": "<r></x>",
}


@requires_oracle
def test_iterparse_raise_parity():
    import defusedxml.ElementTree as DET

    for name, text in ATTACKS.items():
        with pytest.raises(Exception):  # noqa: B017
            list(DET.iterparse(io.StringIO(text)))
        with pytest.raises(Exception):  # purexml: PureXMLError or ParseError
            list(purexml.iterparse(io.StringIO(text)))


def test_iterparse_blocks_are_purexml_errors():
    for name, text in ATTACKS.items():
        if name == "malformed":
            continue
        with pytest.raises(purexml.PureXMLError):
            list(purexml.iterparse(io.StringIO(text)))


def test_no_io_under_streaming():
    """The blocking handlers fire during feed, before iteration proceeds — proven
    with the socket/open/urlopen trip-wire active while consuming the iterator."""
    for text in (ATTACKS["xxe_local"], ATTACKS["xxe_net"]):
        with assert_no_io():
            with pytest.raises(purexml.PureXMLError):
                list(purexml.iterparse(io.StringIO(text)))
            # an IOTouched here would mean a fetch happened — it must not.


# ---- forbid_* knob matrix for iterparse ----
@requires_oracle
def test_iterparse_knob_matrix():
    import defusedxml.ElementTree as DET

    docs = {
        "benign": "<r><a>x</a></r>",
        "internal_dtd": "<!DOCTYPE r [<!ELEMENT r ANY>]><r/>",
        "internal_entity": "<!DOCTYPE r [<!ENTITY e 'v'>]><r>&e;</r>",
        "external_dtd": "<!DOCTYPE r SYSTEM 'http://127.0.0.1:1/x.dtd'><r/>",
    }

    def outcome(fn, text, fd, fe, fx):
        try:
            return ("ok", [(ev, el.tag if hasattr(el, "tag") else el)
                           for ev, el in fn(io.StringIO(text), None, None, fd, fe, fx)])
        except Exception:  # noqa: BLE001
            return ("raise", None)

    for fd, fe, fx in itertools.product([False, True], repeat=3):
        for name, doc in docs.items():
            p = outcome(purexml.iterparse, doc, fd, fe, fx)
            d = outcome(DET.iterparse, doc, fd, fe, fx)
            assert p[0] == d[0], (fd, fe, fx, name, p[0], d[0])
            if p[0] == "ok":
                assert p[1] == d[1], (fd, fe, fx, name)


def test_iterparse_forbid_dtd():
    with pytest.raises(purexml.DTDForbidden):
        list(purexml.iterparse(io.StringIO("<!DOCTYPE r><r/>"), forbid_dtd=True))


# ---- cleanup-on-error through the iterator ----
def test_iterparse_releases_heavy_state_on_error():
    p = purexml.XMLParser()
    with pytest.raises(purexml.PureXMLError):
        list(purexml.iterparse(io.StringIO(ATTACKS["internal_entity"]), parser=p))
    assert p.parser is None and p.target is None


# ---- filename source (opens/closes) + namespace completeness ----
def test_iterparse_from_filename(tmp_path):
    f = tmp_path / "d.xml"
    f.write_text("<r><a>x</a><b/></r>")
    tags = [el.tag for _, el in purexml.iterparse(str(f))]
    assert tags == ["a", "b", "r"]


def test_namespace_now_complete():
    import purexml.ElementTree as PET
    assert hasattr(PET, "iterparse") and "iterparse" in PET.__all__
