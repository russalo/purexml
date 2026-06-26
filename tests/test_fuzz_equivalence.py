"""Differential fuzz: purexml vs the defusedxml oracle (the durability gate).

Seeded → deterministic / CI-stable. Generates diverse XML — allow-path constructs
(nested elements, namespaces, attrs, text, CDATA, comments, PIs, internal DTDs)
*and* attack constructs (entity declarations, external entities/DTDs, entity
references) — and asserts purexml is **C14N-equal-or-both-raise** vs defusedxml for
every input. This is what keeps "equivalent" true as Python/expat/defusedxml drift.

Equivalence is raises-iff-raises + identical-C14N-when-parses. Exception *types*
differ by design (purexml has its own hierarchy), so only the parse-vs-raise *kind*
and the canonical tree are compared.
"""
import random
import xml.etree.ElementTree as ET
from xml.sax.handler import ContentHandler

import pytest

import purexml
from conftest import requires_oracle

_TEXT = ["", "x", "hi there", "  ws  ", "&lt;esc&gt;", "&amp;", "&undef;",
         "<![CDATA[<raw> & ]]>", "café", "&e;",
         "&#65;&#x42;&#67;",                       # decimal + hex char refs
         "&#65;" * 200,                            # char-ref flood (not a bomb)
         "<![CDATA[]]>" "<![CDATA[x]]>",           # adjacent CDATA sections
         "a]]>b",                                  # stray CDATA-close in text
         "\t\n\r mixed ws ", "&#x9;&#xA;",         # whitespace + control char refs
         "&#x10FFFF;", "&#x110000;", "&#0;",       # max-codepoint + out-of-range + null
         "&#xD800;",                               # lone surrogate (invalid char)
         "&lt;&amp;&gt;&quot;&apos;",              # all five predefined entities packed
         "text &lt; <![CDATA[ & raw ]]> tail",     # text/CDATA boundary interleave
         "𝔘𝔫𝔦𝔠𝔬𝔡𝔢",                                  # astral-plane (4-byte UTF-8)
         "  &#32; \t&#9; "]                        # ws char refs amid literal ws
_DOCTYPE = [
    "",                                                              # no dtd
    "<!DOCTYPE root [ <!ELEMENT root ANY> ]>",                       # benign internal dtd
    "<!DOCTYPE root [ <!ELEMENT root ANY><!ATTLIST root a CDATA #IMPLIED> ]>",  # ATTLIST
    "<!DOCTYPE root [ <!NOTATION n SYSTEM 'urn:x'> ]>",              # notation decl (allowed)
    "<!DOCTYPE root [ <!ENTITY e 'expanded'> ]>",                    # internal entity decl (blocked)
    "<!DOCTYPE root [ <!ENTITY e '&e2;&e2;'><!ENTITY e2 'xxxx'> ]>", # mini-bomb (blocked)
    "<!DOCTYPE root [ <!ENTITY %% p 'v'> ]>",                        # param entity decl (blocked)
    "<!DOCTYPE root [ <![IGNORE[ <!ELEMENT x ANY> ]]> ]>",           # conditional section (IGNORE)
    "<!DOCTYPE root [ <![INCLUDE[ <!ELEMENT root ANY> ]]> ]>",       # conditional section (INCLUDE)
    "<!DOCTYPE root [ <!ENTITY e SYSTEM 'file:///no-such-%d'> ]>",   # external entity (blocked)
    "<!DOCTYPE root SYSTEM 'http://127.0.0.1:1/x%d.dtd'>",           # external dtd (allowed, no fetch)
    "<!DOCTYPE root PUBLIC '-//X//Y' 'http://127.0.0.1:1/%d'>",      # public external dtd
    "<!DOCTYPE root [ <!-- dtd comment --><!ELEMENT root ANY> ]>",   # comment inside internal subset
    "<!DOCTYPE root [ <!ENTITY a 'x'><!ENTITY b 'y'><!ENTITY c 'z'> ]>",  # multiple entity decls (blocked)
    "<!DOCTYPE root [ <!ENTITY e '&#38;#60;'> ]>",                   # entity w/ nested char-ref (blocked)
    "<!DOCTYPE root [ <!ELEMENT root ANY><!ATTLIST root a CDATA 'def'> ]>",  # ATTLIST w/ default value
    "<!DOCTYPE root [ <!ENTITY %% p SYSTEM 'http://127.0.0.1:1/p%d.dtd'> ]>",  # external param entity (blocked on ref; decl alone)
]


def _elem(rng, depth):
    tag = rng.choice(["a", "b", "c", "n:x", "item"])
    # Accumulate into a dict so a repeated name doesn't emit a duplicate attribute
    # (a well-formedness violation that makes both parsers raise early, wasting the
    # document on the error path instead of exploring deeper parse paths — PR#8 Gemini).
    attr_map = {}
    for _ in range(rng.randint(0, 3)):
        attr_map[rng.choice(["k", "id", "n:at", "xml:lang"])] = rng.choice(
            ["1", "v", "café", "a&amp;b", "&lt;x&gt;", "&#65;z", ""])
    attrs = "".join(" %s=%r" % (k, v) for k, v in attr_map.items())
    body = ""
    n = 0 if depth >= 4 else rng.randint(0, 3)
    if n == 0:
        body = rng.choice(_TEXT)
    else:
        for _ in range(n):
            r = rng.random()
            if r < 0.15:
                body += "<!-- c -->"
            elif r < 0.25:
                body += "<?pi go?>"
            else:
                body += _elem(rng, depth + 1)
    return "<%s%s>%s</%s>" % (tag, attrs, body, tag)


def _doc(rng):
    s = ""
    if rng.random() < 0.6:
        ver = rng.choice(["1.0", "1.1"])
        enc = rng.choice([" encoding='UTF-8'", " encoding='utf-8'", " encoding='ISO-8859-1'", ""])
        s += "<?xml version='%s'%s?>" % (ver, enc)
    dt = rng.choice(_DOCTYPE)
    if "%d" in dt:
        dt = dt % rng.randint(0, 9)
    s += dt
    # root is named 'root' (matches DOCTYPE); declare the n: namespace so n:* is well-formed
    inner = "".join(_elem(rng, 1) for _ in range(rng.randint(1, 3)))
    s += "<root xmlns:n='urn:n'>%s</root>" % inner
    return s


def _kind(fn, s):
    # Catch only the parse call: a parse-success-but-serialize-failure must surface
    # rather than masquerade as a parse failure (else a serialization divergence
    # would hide behind both-raise — PR#8 Gemini).
    try:
        tree = fn(s)
    except Exception:  # noqa: BLE001 — kind, not type, is what matters
        return ("raise", None)
    return ("parse", ET.canonicalize(ET.tostring(tree, encoding="unicode")))


#: Fuzz dimensions — single source of truth, also read by the equivalence-report
#: generator (scratch/review/gen_equivalence_report.py) so the published doc count
#: can never drift from what the test actually runs.
SEEDS = 12
PER_SEED = 80  # SEEDS × PER_SEED = 960 documents (× 2 for str+bytes)


@requires_oracle
@pytest.mark.parametrize("seed", range(SEEDS))
def test_differential_fuzz(seed):
    import defusedxml.ElementTree as DET

    rng = random.Random(seed * 1000 + 17)
    for _ in range(PER_SEED):
        doc = _doc(rng)
        for arg in (doc, doc.encode("utf-8")):  # str AND bytes
            pk = _kind(purexml.fromstring, arg)
            dk = _kind(DET.fromstring, arg)
            assert pk[0] == dk[0], (arg, pk[0], dk[0])
            if pk[0] == "parse":
                assert pk[1] == dk[1], ("C14N differs", arg)


# -- the same differential gate, extended to the breadth surfaces (v0.13.1) ----------
# The equivalence claim covers every drop-in surface, not just ElementTree: minidom by
# DOM serialization, sax by the event stream, xmlrpc by block-parity. Same `_doc` fuzzer.

class _SaxRec(ContentHandler):
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


def _minidom_kind(mod, s):
    try:
        doc = mod.parseString(s)
    except Exception:  # noqa: BLE001
        return ("raise", None)
    return ("parse", doc.toxml())  # both build the same stdlib Document -> identical toxml


def _sax_kind(mod, b):
    h = _SaxRec()
    try:
        mod.parseString(b, h)
    except Exception:  # noqa: BLE001
        return ("raise", None)
    return ("parse", tuple(h.ev))


@requires_oracle
@pytest.mark.parametrize("seed", range(SEEDS))
def test_differential_fuzz_minidom(seed):
    import defusedxml.minidom as DM

    rng = random.Random(seed * 1000 + 23)
    for _ in range(PER_SEED):
        doc = _doc(rng)
        for arg in (doc, doc.encode("utf-8")):  # minidom accepts str AND bytes
            pk = _minidom_kind(purexml.minidom, arg)
            dk = _minidom_kind(DM, arg)
            assert pk[0] == dk[0], (arg, pk[0], dk[0])
            if pk[0] == "parse":
                assert pk[1] == dk[1], ("minidom DOM differs", arg)


@requires_oracle
@pytest.mark.parametrize("seed", range(SEEDS))
def test_differential_fuzz_sax(seed):
    import defusedxml.sax as DS

    rng = random.Random(seed * 1000 + 29)
    for _ in range(PER_SEED):
        b = _doc(rng).encode("utf-8")  # sax is bytes-only
        pk = _sax_kind(purexml.sax, b)
        dk = _sax_kind(DS, b)
        assert pk[0] == dk[0], (b, pk[0], dk[0])
        if pk[0] == "parse":
            assert pk[1] == dk[1], ("sax events differ", b)


@requires_oracle
@pytest.mark.parametrize("seed", range(SEEDS))
def test_differential_fuzz_xmlrpc_block_parity(seed):
    # xmlrpc's value (vs minidom/sax) is the *block decision* — its defused parser must refuse
    # iff defusedxml's does. (The unmarshalled value path is stdlib + identical; arbitrary fuzz
    # isn't valid xmlrpc, so we compare the security decision, not the result.)
    import defusedxml.xmlrpc as DX
    from defusedxml.common import DefusedXmlException

    pcls = purexml.xmlrpc._build_defused_parser_cls()
    dcls = DX.DefusedExpatParser

    class _T:
        def __getattr__(self, n):
            return lambda *a, **k: None

    def blocked(cls, s, block_exc):
        p = cls(_T())
        try:
            p.feed(s)
            p.close()
            return False
        except block_exc:
            return True
        except Exception:  # noqa: BLE001 — a non-block error (unmarshaller etc.) is "not blocked"
            return False

    rng = random.Random(seed * 1000 + 31)
    for _ in range(PER_SEED):
        doc = _doc(rng)
        for arg in (doc, doc.encode("utf-8")):  # xmlrpc payloads are bytes over HTTP; test both
            assert blocked(pcls, arg, purexml.PureXMLError) == blocked(dcls, arg, DefusedXmlException), \
                ("xmlrpc block decision differs", arg)
