"""Malformed handling, version-surface sync, and zero-runtime-dependency guard."""
import pathlib
import xml.etree.ElementTree as ET

import pytest

import purexml


def test_py_typed_marker_shipped():
    """PEP 561 marker must sit in the package so downstream type-checkers use our
    types (v0.8). Guards against it being dropped from the package/wheel."""
    marker = pathlib.Path(purexml.__file__).resolve().parent / "py.typed"
    assert marker.is_file(), "py.typed marker missing — typed package guarantee broken"


def test_malformed_raises_parseerror():
    with pytest.raises(ET.ParseError):
        purexml.fromstring("<r><a></r>")


def test_malformed_is_not_a_purexml_block():
    """Malformed != a security block: it is the stdlib ParseError (not ValueError)."""
    with pytest.raises(ET.ParseError) as exc:
        purexml.fromstring("<unclosed>")
    assert not isinstance(exc.value, purexml.PureXMLError)


def test_version_surface_sync():
    """CONVENTIONS §1.4: in-code __version__ matches the manifest."""
    root = pathlib.Path(__file__).resolve().parent.parent
    pyproject = (root / "pyproject.toml").read_text()
    # crude but dependency-free: find the [project] version line
    line = next(ln for ln in pyproject.splitlines() if ln.strip().startswith("version ="))
    manifest_version = line.split("=", 1)[1].strip().strip('"')
    assert purexml.__version__ == manifest_version


def test_version_is_plain_string():
    """FO consumer floor (2026-06-26): __version__ must be a stable plain `str` — FO reads it
    into ScanContext + a manifest checksum, and a non-string/odd-repr breaks its determinism."""
    assert type(purexml.__version__) is str


def test_fromstring_element_walk_equivalent_to_stdlib():
    """FO consumer floor (2026-06-26): on an allowed parse, `fromstring` must return a tree
    byte-identical to stdlib `xml.etree.ElementTree` on the shape FO reads — `.iter(tag)` ORDER,
    `.text`, attributes, and namespace-qualified tags — not only C14N-string-equal. A silent
    element-walk divergence would shift FO's manifest VALUES."""
    doc = ('<root xmlns:n="urn:x" xmlns="urn:d">'
           '<n:c a="1" b="2">hi</n:c><d><e>x</e>tail</d><c k="v"/></root>')
    px = purexml.fromstring(doc)
    std = ET.fromstring(doc)

    def walk(el):
        return [(e.tag, e.text, e.tail, tuple(sorted(e.attrib.items()))) for e in el.iter()]

    assert walk(px) == walk(std)
    # the specific accessors FO uses, on a namespaced element
    assert px.find("{urn:x}c").get("a") == std.find("{urn:x}c").get("a") == "1"
    assert [e.text for e in px.iter("{urn:d}e")] == [e.text for e in std.iter("{urn:d}e")]


def test_no_runtime_dependency_on_defusedxml():
    """src/ must never IMPORT defusedxml (it is a dev/test oracle only).

    Checks import statements, not prose — the design docstrings legitimately
    mention defusedxml as the behavioral reference.
    """
    src = pathlib.Path(purexml.__file__).resolve().parent
    for py in src.rglob("*.py"):
        for line in py.read_text().splitlines():
            stripped = line.strip()
            assert not stripped.startswith(("import defusedxml", "from defusedxml")), py
    # And no third-party runtime imports at all: the only non-stdlib name allowed
    # is the package's own relative imports.
    import purexml._parser as _p
    assert _p.__name__.startswith("purexml")


def test_no_reference_cycle_after_parse():
    """Regression (PR#1 Gemini finding): the hardened parser must be reclaimable by
    refcounting alone — no expat-parser<->self cycle that defers cleanup to GC."""
    import gc
    import weakref

    from purexml._parser import XMLParser

    gc.disable()
    try:
        p = XMLParser()
        ref = weakref.ref(p)
        p.feed("<r><a>x</a></r>")
        p.close()
        del p
        assert ref() is None, "reference cycle: instance not freed by refcounting"
    finally:
        gc.enable()


def test_public_api_surface():
    assert set(purexml.__all__) >= {
        "fromstring", "PureXMLError", "EntitiesForbidden",
        "ExternalReferenceForbidden", "ParseError",
    }
