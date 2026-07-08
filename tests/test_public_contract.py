"""The 1.0 public contract, as a mechanical guard.

`PUBLIC_CONTRACT.md` froze the STABLE surface at v1.0.0; `docs/v1.0.0_RFC_Specification.md`
enumerates it. This test snapshots that surface so it cannot silently drift — a removed
symbol, a renamed/reordered parameter, a changed default, or a changed exception hierarchy
fails CI as a **contract break** (which would require a 2.0). The PROVISIONAL surface
(`Limits`, `security_report`, the version-assertion knobs) is deliberately *not* pinned here.
"""
import inspect

import pytest

import purexml
from purexml import ElementTree, common, minidom, sax, xmlrpc
from purexml import errors


# --- 3.1 module namespaces (the s/defusedxml/purexml/ contract) ---
def test_module_namespaces_present():
    for mod in ("ElementTree", "minidom", "sax", "expatreader", "xmlrpc", "common"):
        assert hasattr(purexml, mod), f"purexml.{mod} must be a public namespace"


# --- 3.2 function surface + signatures (defaults are contract) ---
STABLE_ET = ["fromstring", "parse", "iterparse", "fromstringlist", "XMLParser",
             "XML", "XMLParse", "XMLTreeBuilder", "tostring", "ParseError"]


@pytest.mark.parametrize("name", STABLE_ET)
def test_elementtree_surface_present(name):
    assert hasattr(ElementTree, name), f"purexml.ElementTree.{name} is frozen surface"


def _forbid_defaults(fn):
    """The frozen forbid_* defaults + keyword-only `limits` on a parse entry point."""
    p = inspect.signature(fn).parameters
    assert p["forbid_dtd"].default is False
    assert p["forbid_entities"].default is True
    assert p["forbid_external"].default is True
    assert p["limits"].kind is inspect.Parameter.KEYWORD_ONLY
    assert p["limits"].default is None


@pytest.mark.parametrize("name", ["fromstring", "parse", "iterparse", "fromstringlist"])
def test_elementtree_defaults_frozen(name):
    _forbid_defaults(getattr(ElementTree, name))


@pytest.mark.parametrize("name", ["parse", "iterparse", "fromstringlist"])
def test_elementtree_parser_param_frozen(name):
    # these carry the stdlib `parser=None` param (fromstring does not) — frozen signature
    p = inspect.signature(getattr(ElementTree, name)).parameters
    assert "parser" in p and p["parser"].default is None


def test_fromstring_accepts_str_and_bytes_param():
    # first positional parameter is the text/bytes payload
    first = list(inspect.signature(ElementTree.fromstring).parameters)[0]
    assert first == "text"


def test_xmlparser_is_keyword_only_and_forbid_defaults():
    p = inspect.signature(ElementTree.XMLParser).parameters
    # XMLParser is fully keyword-only (`def __init__(self, *, ...)`) — frozen shape
    assert all(v.kind is inspect.Parameter.KEYWORD_ONLY for v in p.values()), \
        f"XMLParser params must stay keyword-only: {[(k, v.kind) for k, v in p.items()]}"
    assert p["forbid_dtd"].default is False
    assert p["forbid_entities"].default is True
    assert p["forbid_external"].default is True


def test_toplevel_convenience_reexports():
    # `from purexml import fromstring` (etc.) — Stable alongside the mirror namespaces,
    # including the public exception classes (all in __init__.__all__).
    for name in ("fromstring", "parse", "iterparse", "fromstringlist", "XMLParser",
                 "XML", "tostring", "ParseError", "__version__",
                 "PureXMLError", "DTDForbidden", "EntitiesForbidden",
                 "ExternalReferenceForbidden", "NotSupportedError"):
        assert hasattr(purexml, name), f"purexml.{name} is frozen top-level surface"
    assert purexml.fromstring is ElementTree.fromstring


def test_minidom_surface():
    assert callable(minidom.parse) and callable(minidom.parseString)
    p = inspect.signature(minidom.parseString).parameters
    assert "string" in p  # accepts str|bytes (unlike sax which is bytes-only)
    assert p["forbid_dtd"].default is False
    assert p["forbid_entities"].default is True
    assert p["forbid_external"].default is True
    assert p["limits"].kind is inspect.Parameter.KEYWORD_ONLY and p["limits"].default is None


def test_sax_surface():
    for name in ("make_parser", "parse", "parseString"):
        assert callable(getattr(sax, name))


def test_xmlrpc_surface():
    for name in ("monkey_patch", "unmonkey_patch", "defused_gzip_decode", "MAX_DATA"):
        assert hasattr(xmlrpc, name)


# --- 3.3 exception hierarchy — COMPLETE + frozen ---
def test_exception_hierarchy_is_exactly_the_frozen_set():
    base = errors.PureXMLError
    assert issubclass(base, ValueError)
    # PureXMLError's direct block-exception children (order-independent)
    direct = {c.__name__ for c in base.__subclasses__()}
    assert direct == {
        "DTDForbidden", "EntitiesForbidden", "ExternalReferenceForbidden",
        "NotSupportedError", "LimitExceeded",
    }, f"exception set drifted: {direct}"
    # LimitExceeded's children (opt-in, provisional-but-typed)
    limit_kids = {c.__name__ for c in errors.LimitExceeded.__subclasses__()}
    assert limit_kids == {"DepthExceeded", "AttributesExceeded", "SizeExceeded"}
    # every refusal is a ValueError
    for exc in (errors.DTDForbidden, errors.EntitiesForbidden,
                errors.ExternalReferenceForbidden, errors.NotSupportedError,
                errors.LimitExceeded, errors.DepthExceeded,
                errors.AttributesExceeded, errors.SizeExceeded):
        assert issubclass(exc, ValueError)


def test_common_defusedxml_alias_frozen():
    assert common.DefusedXmlException is errors.PureXMLError


def test_malformed_raises_stdlib_error_per_surface():
    """Frozen exception contract: malformed input raises the underlying stdlib parser's
    error for that surface — never a PureXMLError."""
    import xml.etree.ElementTree as _ET
    import xml.parsers.expat as _expat
    from xml.sax import SAXParseException
    from xml.sax.handler import ContentHandler

    bad = "<r><a></r>"
    cases = [
        (lambda: ElementTree.fromstring(bad), _ET.ParseError),
        (lambda: minidom.parseString(bad), _expat.ExpatError),
        (lambda: sax.parseString(bad.encode(), ContentHandler()), SAXParseException),
    ]
    for call, exc in cases:
        with pytest.raises(exc) as ei:
            call()
        assert not isinstance(ei.value, errors.PureXMLError)


# --- 3.6 __version__ ---
def test_version_is_plain_str():
    assert isinstance(purexml.__version__, str) and purexml.__version__
