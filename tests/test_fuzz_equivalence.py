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

import pytest

import purexml
from conftest import requires_oracle

_TEXT = ["", "x", "hi there", "  ws  ", "&lt;esc&gt;", "&amp;", "&undef;",
         "<![CDATA[<raw> & ]]>", "café", "&e;",
         "&#65;&#x42;&#67;",                       # decimal + hex char refs
         "&#65;" * 200,                            # char-ref flood (not a bomb)
         "<![CDATA[]]>" "<![CDATA[x]]>",           # adjacent CDATA sections
         "a]]>b",                                  # stray CDATA-close in text
         "\t\n\r mixed ws ", "&#x9;&#xA;"]         # whitespace + control char refs
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
]


def _elem(rng, depth):
    tag = rng.choice(["a", "b", "c", "n:x", "item"])
    attrs = ""
    for _ in range(rng.randint(0, 2)):
        attrs += " %s=%r" % (rng.choice(["k", "id", "n:at"]), rng.choice(["1", "v", "café"]))
    body = ""
    n = 0 if depth >= 3 else rng.randint(0, 3)
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
    try:
        return ("parse", ET.canonicalize(ET.tostring(fn(s), encoding="unicode")))
    except Exception:  # noqa: BLE001 — kind, not type, is what matters
        return ("raise", None)


@requires_oracle
@pytest.mark.parametrize("seed", range(8))
def test_differential_fuzz(seed):
    import defusedxml.ElementTree as DET

    rng = random.Random(seed * 1000 + 17)
    for _ in range(60):  # 8 seeds × 60 = 480 documents
        doc = _doc(rng)
        for arg in (doc, doc.encode("utf-8")):  # str AND bytes
            pk = _kind(purexml.fromstring, arg)
            dk = _kind(DET.fromstring, arg)
            assert pk[0] == dk[0], (arg, pk[0], dk[0])
            if pk[0] == "parse":
                assert pk[1] == dk[1], ("C14N differs", arg)
