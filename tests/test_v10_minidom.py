"""v0.10 — `purexml.minidom` drop-in + `purexml.common` compat shim.

minidom returns a standard `xml.dom.minidom.Document`; hardening rides on a subclass of
the stdlib expatbuilder, so allow-path output is identical to the oracle and attacks block
with purexml's exceptions. The falsify-first rules carry over: same parses succeed
(oracle-equal `toxml()`), same attacks blocked (a `PureXMLError`), no I/O on untrusted input.
"""
import pytest

import purexml
import purexml.common as PC
import purexml.minidom as PM
from conftest import ALLOW_CASES, assert_no_io, requires_oracle


def test_parsestring_returns_document():
    doc = PM.parseString("<r><a>x</a><b k='v'>y</b></r>")
    assert doc.documentElement.tagName == "r"
    assert doc.documentElement.getElementsByTagName("b")[0].getAttribute("k") == "v"


def test_parse_file_roundtrip(tmp_path):
    p = tmp_path / "d.xml"
    p.write_text("<r><a>x</a></r>")
    # filename form (opens the caller's file) and open-file form both work.
    assert PM.parse(str(p)).documentElement.tagName == "r"
    with open(p, "rb") as fp:
        assert PM.parse(fp).documentElement.tagName == "r"


@pytest.mark.parametrize("name", [
    "internal_general_entity", "internal_param_entity", "billion_laughs",
    "xxe_local_file", "xxe_network", "xxe_param_external_dtd",
])
def test_attacks_block_with_purexml_exception_no_io(name, attack_cases):
    # Each attack must raise a purexml refusal (a ValueError) AND touch no I/O — the
    # block fires at the entity declaration, before any expansion/resolution.
    src = attack_cases[name]
    with assert_no_io():
        with pytest.raises(purexml.PureXMLError):
            PM.parseString(src)


def test_unparsed_ndata_entity_blocked():
    # NDATA entities go through expat's UnparsedEntityDeclHandler (a distinct path from
    # the general EntityDeclHandler) — purexml's minidom builder blocks it too.
    ndata = ('<?xml version="1.0"?><!DOCTYPE r [ <!NOTATION gif SYSTEM "g">'
             '<!ENTITY pic SYSTEM "file:///etc/hostname" NDATA gif> ]><r/>')
    with assert_no_io():
        with pytest.raises(purexml.EntitiesForbidden):
            PM.parseString(ndata)


def test_external_ref_backstop_when_entities_allowed():
    # With forbid_entities=False the external-entity DECLARATION is allowed, so the
    # external-reference handler is the backstop that fires on resolution — proving the
    # no-fetch guarantee does not depend solely on entity-declaration blocking.
    ext = ('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/hostname"> ]>'
           '<r>&x;</r>')
    with assert_no_io():
        with pytest.raises(purexml.ExternalReferenceForbidden):
            PM.parseString(ext, forbid_entities=False)


@pytest.mark.parametrize("src", [
    '<?xml version="1.0"?><!DOCTYPE r SYSTEM "http://127.0.0.1:1/x.dtd"><r/>',
    '<?xml version="1.0"?><!DOCTYPE r SYSTEM "http://127.0.0.1:1/x.dtd"><r><a>x</a></r>',
    '<?xml version="1.0"?><!DOCTYPE r PUBLIC "-//X//DTD//EN" "http://127.0.0.1:1/x.dtd"><r/>',
])
def test_external_dtd_allowed_but_never_fetched(src):
    # F2 on the DOM surface: an UNRESOLVED external DTD parses (default forbid_dtd=False)
    # and triggers NO I/O — a DOM builder is exactly where external-subset loading could
    # sneak a fetch in. The assert_no_io trip-wire proves it doesn't.
    with assert_no_io():
        assert PM.parseString(src).documentElement.tagName == "r"


def test_forbid_dtd_raises_dtdforbidden():
    # A DOCTYPE with no entities parses by default (forbid_dtd=False) but is refused
    # when the caller opts into the strict OWASP mode.
    doc_with_dtd = '<?xml version="1.0"?><!DOCTYPE r [ <!ELEMENT r (#PCDATA)> ]><r>ok</r>'
    assert PM.parseString(doc_with_dtd).documentElement.tagName == "r"  # default: allowed
    with pytest.raises(purexml.DTDForbidden):
        PM.parseString(doc_with_dtd, forbid_dtd=True)


def test_no_reference_cycle_on_minidom_error():
    # PR#28 Codex: a malformed/blocked DOM payload must not leave a builder<->parser cycle
    # for cyclic GC — the builder must be reclaimable by refcounting alone, matching the
    # ElementTree path's guarantee. (The stdlib ExpatBuilder only clears _parser on success.)
    import gc
    import weakref

    from purexml.minidom import _DefusedExpatBuilderNS

    gc.disable()
    try:
        for payload in ("<r>",  # malformed
                        '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x "v"> ]><r>&x;</r>'):  # blocked
            b = _DefusedExpatBuilderNS()
            ref = weakref.ref(b)
            try:
                b.parseString(payload)
            except Exception:  # noqa: BLE001
                pass
            del b
            assert ref() is None, "builder<->parser cycle survived refcounting on error path"
    finally:
        gc.enable()


def test_custom_parser_not_supported():
    # A caller-supplied parser would bypass hardening — refused, not honored.
    with pytest.raises(purexml.NotSupportedError):
        PM.parseString("<r/>", parser=object())
    with pytest.raises(purexml.NotSupportedError):
        PM.parse("ignored.xml", parser=object())


def test_common_shim_is_drop_in_for_catch_sites():
    # `from defusedxml.common import DefusedXmlException` -> `from purexml.common import ...`
    # must keep `except DefusedXmlException` working: the alias IS purexml's base.
    assert PC.DefusedXmlException is purexml.PureXMLError
    for name in ("EntitiesForbidden", "ExternalReferenceForbidden", "DTDForbidden",
                 "NotSupportedError"):
        assert hasattr(PC, name)
    # a real block is catchable under the defusedxml name
    bomb = ('<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x "v"> ]><r>&x;</r>')
    try:
        PM.parseString(bomb)
    except PC.DefusedXmlException:
        pass
    else:
        pytest.fail("entity bomb was not blocked / not catchable as DefusedXmlException")


# -- oracle-gated parity (the equivalence guarantee) --------------------------------

@requires_oracle
def test_path_object_matches_oracle_rejection(tmp_path):
    # Deliberate parity (PR#28 Gemini — declined with grounding): stdlib xml.dom.minidom.parse
    # AND defusedxml.minidom.parse both REJECT a pathlib.Path (str-only file handling); purexml
    # matches them. Accepting a Path would over-support beyond the oracle and DIVERGE from the
    # strict-mirror contract. This pins the parity so a future "fix" can't silently regress it.
    import defusedxml.minidom as DM

    p = tmp_path / "d.xml"
    p.write_text("<r/>")
    with pytest.raises(Exception) as oracle_exc:  # noqa: BLE001, PT011
        DM.parse(p)
    with pytest.raises(type(oracle_exc.value)):
        PM.parse(p)


@requires_oracle
@pytest.mark.parametrize("name", list(ALLOW_CASES))
def test_minidom_allow_parity_with_oracle(name):
    import defusedxml.minidom as DM

    src = ALLOW_CASES[name]
    # Both build a standard stdlib Document via the same ExpatBuilder; purexml only adds
    # blocking (which doesn't fire here) -> identical serialization. (Both-raise also OK,
    # e.g. an external-ref case, as long as purexml's refusal is a PureXMLError.)
    oracle_doc = oracle_err = None
    try:
        oracle_doc = DM.parseString(src)
    except Exception as e:  # noqa: BLE001
        oracle_err = e
    if oracle_err is not None:
        with pytest.raises(purexml.PureXMLError):
            PM.parseString(src)
    else:
        assert PM.parseString(src).toxml() == oracle_doc.toxml()


@requires_oracle
@pytest.mark.parametrize("name", [
    "internal_general_entity", "internal_param_entity", "billion_laughs",
    "xxe_local_file", "xxe_network", "xxe_param_external_dtd",
])
def test_minidom_block_parity_with_oracle(name, attack_cases):
    from defusedxml.common import DefusedXmlException
    import defusedxml.minidom as DM

    src = attack_cases[name]
    with pytest.raises(DefusedXmlException):
        DM.parseString(src)
    with pytest.raises(purexml.PureXMLError):
        PM.parseString(src)
