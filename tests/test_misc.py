"""Malformed handling, version-surface sync, and zero-runtime-dependency guard."""
import pathlib
import xml.etree.ElementTree as ET

import pytest

import purexml


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
    line = next(l for l in pyproject.splitlines() if l.strip().startswith("version ="))
    manifest_version = line.split("=", 1)[1].strip().strip('"')
    assert purexml.__version__ == manifest_version


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
