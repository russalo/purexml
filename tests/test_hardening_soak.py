"""Adversarial soak — red-team vectors beyond the core battery (patch hardening).

The core 6 attack cases live in `conftest._attack_cases`; the 2 expat-layer classes
in `test_durability.py`. This module adds decorrelated red-team vectors, each
**grounded** (constructed + confirmed equivalent to the defusedxml oracle before being
codified): distinct DoS classes, the unparsed-entity path, and — the highest-value
addition — **encoding-vector** attacks (UTF-16 / BOM bytes) proving the block is
encoding-independent (a real bypass class in parsers that scan only decoded text).

Invariant unchanged: purexml blocks iff defusedxml blocks, the refusal is a
`PureXMLError`/`ValueError`, no I/O occurs, and allow-path inputs stay C14N-equal.
"""
import xml.etree.ElementTree as ET

import pytest

import purexml
from conftest import assert_no_io, requires_oracle

# --- BLOCK-path soak: each MUST raise EntitiesForbidden, no I/O, any encoding ---
_BL_UTF16 = (
    '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE lolz [ <!ENTITY lol "lol">'
    '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;"> ]><lolz>&lol2;</lolz>'
).encode("utf-16")
_XXE = ('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/hostname"> ]>'
        '<r>&x;</r>')

BLOCK_VECTORS = {
    # Quadratic blowup — ONE big entity referenced many times (distinct from the
    # exponential billion-laughs); blocked at the entity declaration all the same.
    "quadratic_blowup":
        '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY a "%s"> ]><r>%s</r>'
        % ("A" * 1000, "&a;" * 1000),
    # Unparsed entity (NDATA / NOTATION) — exercises the UnparsedEntityDeclHandler path.
    "unparsed_ndata_entity":
        '<?xml version="1.0"?><!DOCTYPE r [ <!NOTATION gif SYSTEM "image/gif">'
        '<!ENTITY pic SYSTEM "file:///etc/hostname" NDATA gif> ]><r/>',
    # Sub-amplification-cap nested bomb — expands without tripping libexpat's cap;
    # proves the block is PROACTIVE (at declaration), not reliant on the expat cap.
    "nested_entity_subcap":
        '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY a "x"><!ENTITY b "&a;&a;">'
        '<!ENTITY c "&b;&b;"> ]><r>&c;</r>',
    # External parameter entity (two-stage XXE setup) — blocked at declaration.
    "param_entity_external":
        '<?xml version="1.0"?><!DOCTYPE r [ '
        '<!ENTITY % ext SYSTEM "http://127.0.0.1:1/evil.dtd"> %ext; ]><r/>',
    # Encoding-vector: billion-laughs as UTF-16 BYTES — block must be encoding-independent.
    "billion_laughs_utf16_bytes": _BL_UTF16,
    # Encoding-vector: XXE behind a UTF-8 BOM (bytes).
    "xxe_utf8_bom_bytes": b"\xef\xbb\xbf" + _XXE.encode("utf-8"),
}

# --- ALLOW-path soak: each MUST parse C14N-equal to the oracle (encoding/ns edges) ---
ALLOW_VECTORS = {
    "valid_utf16_bytes":
        '<?xml version="1.0" encoding="UTF-16"?><r><a>x</a></r>'.encode("utf-16"),
    "valid_utf8_bom_bytes": b"\xef\xbb\xbf" + "<r>ok</r>".encode("utf-8"),
    "default_ns_redefinition": '<r xmlns="urn:a"><c xmlns="urn:b"><d/></c></r>',
    "xml_reserved_attrs": '<r xml:lang="en" xml:space="preserve"> text </r>',
}


@pytest.mark.parametrize("name", list(BLOCK_VECTORS))
def test_block_vector_raises_entitiesforbidden_no_io(name):
    with assert_no_io():
        with pytest.raises(purexml.EntitiesForbidden):
            purexml.fromstring(BLOCK_VECTORS[name])


@requires_oracle
@pytest.mark.parametrize("name", list(BLOCK_VECTORS))
def test_block_vector_parity_with_oracle(name):
    from defusedxml.common import DefusedXmlException
    import defusedxml.ElementTree as DET

    with pytest.raises(DefusedXmlException):
        DET.fromstring(BLOCK_VECTORS[name])


@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_VECTORS))
def test_allow_vector_c14n_equal_to_oracle(name):
    import defusedxml.ElementTree as DET

    arg = ALLOW_VECTORS[name]
    p = ET.canonicalize(ET.tostring(purexml.fromstring(arg), encoding="unicode"))
    d = ET.canonicalize(ET.tostring(DET.fromstring(arg), encoding="unicode"))
    assert p == d


def test_encoding_vector_block_is_encoding_independent():
    """The same billion-laughs blocks whether delivered as str, UTF-8 bytes, or
    UTF-16 bytes — the refusal is at the entity declaration, before decoding matters."""
    src = ('<?xml version="1.0"?><!DOCTYPE lolz [ <!ENTITY lol "lol">'
           '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;"> ]><lolz>&lol2;</lolz>')
    # UTF-16 bytes carry a BOM → expat auto-detects the encoding; the block still
    # fires at the entity declaration, before decoding matters.
    for arg in (src, src.encode("utf-8"), src.encode("utf-16")):
        with pytest.raises(purexml.EntitiesForbidden):
            purexml.fromstring(arg)
