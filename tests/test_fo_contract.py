"""The file-observer (fo) consumer contract — an executable CI gate.

fo adopts purexml by dropping its optional ``defusedxml`` dependency: it calls exactly
``from purexml.ElementTree import fromstring`` (aliased over a stdlib fallback) to harden
the XML parse in its OOXML specialists (docx/xlsx/pptx/odt/ods/odp) and its XML-keys
extraction, then walks the result with flat, iterative access. fo's steward relayed a
six-point contract (2026-07). This module encodes each point so that any future change
which would break fo's adoption fails CI **as a named FO regression**, not silently —
turning a relayed promise into an enforced guarantee.

The points (fo's priority order); each maps to a ``test_fo_<n>_*`` below:
  1. bytes AND str parity — raw bytes honor the in-prolog encoding declaration (fo passes
     bytes on purpose so the parser reads the encoding decl; a pre-decoded str trips
     stdlib ElementTree on a doc with an encoding decl).
  2. never-crash + never-HANG on hostile input — the classic non-terminating bombs are
     blocked by DEFAULT (no knobs, parity with defusedxml); opt-in ``RECOMMENDED_LIMITS``
     bounds structural DoS with typed, catchable raises. The bounded-TIME evidence
     (never-hang, measured, not asserted) is ``test_fo_2_bounded_time_*``.
  3. the ``defusedxml.common`` exception types — ``except DefusedXmlException`` catches a
     purexml refusal after a literal ``s/defusedxml/purexml/``.
  4. determinism — identical input → identical tree (stable, document-order attributes;
     no dict/set-order leakage).
  5. the 3.10 floor + fo's exact flat read surface (``.tag`` Clark-notation, ``.iter(tag)``,
     ``.get``, ``.text``, child iteration) stay supported.
  6. ``purexml.__version__`` is a plain ``str`` (fo stamps it into
     ``ScanContext.dependencies`` and a manifest checksum; a non-string/odd-repr broke
     determinism before).

fo's raw-bytes docProps case is already a named test in ``test_equivalence.py``; this
module extends that coupling to the whole contract. See
``docs/FO_REQUIRED_COMPATIBILITY.md`` §1a for the relayed contract.
"""
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import purexml
from purexml import RECOMMENDED_LIMITS
# fo's EXACT import path — a rename/restructure here breaks fo's installs AND its
# ScanContext.dependencies determinism fingerprint. Import it the way fo does.
from purexml.ElementTree import fromstring
from purexml.errors import (
    AttributesExceeded,
    DepthExceeded,
    EntitiesForbidden,
    LimitExceeded,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _c14n(elem):
    """C14N string of a *small* tree (do NOT call on the deep-nesting inputs — serializing
    a >1000-deep tree recursively is the RecursionError this contract documents)."""
    return ET.canonicalize(ET.tostring(elem, encoding="unicode"))


# The classic non-terminating bomb + an XXE, blocked by DEFAULT (declaration-time).
BILLION_LAUGHS = (
    '<?xml version="1.0"?><!DOCTYPE lolz [ <!ENTITY lol "lol">'
    '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
    '<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
    ' ]><lolz>&lol3;</lolz>'
)
XXE_NETWORK = (
    '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "http://127.0.0.1:1/x"> ]>'
    '<r>&x;</r>'
)


# ---------------------------------------------------------------------------
# Point 0 — the adoption surface itself: fo pins this exact import path.
# ---------------------------------------------------------------------------
def test_fo_import_path_is_stable():
    """fo pins ``from purexml.ElementTree import fromstring``. Guard the exact path now —
    FO_REQUIRED_COMPATIBILITY §1a #1: any rename must land BEFORE fo pins, not after."""
    import purexml.ElementTree as et_mod

    assert hasattr(et_mod, "fromstring")
    assert et_mod.fromstring is fromstring


# ---------------------------------------------------------------------------
# Point 1 — bytes AND str parity, encoding declaration honored on bytes.
# ---------------------------------------------------------------------------
def test_fo_1_bytes_with_encoding_declaration_parses():
    """docProps/app.xml-style: bytes carrying an in-prolog encoding decl must parse (NOT
    the C parser's str-only ``ValueError``). This is precisely why fo passes raw bytes."""
    raw = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<Properties><Application>x</Application></Properties>').encode("utf-8")
    root = fromstring(raw)
    assert next(root.iter("Application")).text == "x"


def test_fo_1_str_and_bytes_yield_identical_tree():
    """fo passes str elsewhere and bytes for docProps. On the same content both must
    produce the same tree (C14N-identical)."""
    text = "<Properties><Application>x</Application><Company>acme</Company></Properties>"
    assert _c14n(fromstring(text)) == _c14n(fromstring(text.encode("utf-8")))


# ---------------------------------------------------------------------------
# Point 2 — never-crash + never-HANG; default-safe bombs; opt-in typed caps.
# ---------------------------------------------------------------------------
def test_fo_2_billion_laughs_blocked_by_default():
    """The classic non-terminating bomb is refused at the entity DECLARATION, before any
    expansion — by DEFAULT (no knobs, parity with defusedxml). Catchable ``ValueError``."""
    with pytest.raises(EntitiesForbidden) as ei:
        fromstring(BILLION_LAUGHS)
    assert isinstance(ei.value, ValueError)


def test_fo_2_xxe_blocked_by_default():
    """An external-entity (XXE) declaration is refused by DEFAULT — at the entity
    DECLARATION, before external resolution is ever attempted (so it surfaces as
    ``EntitiesForbidden``, not the untriggered ``ExternalReferenceForbidden`` backstop;
    see LIMITATIONS.md). Assert the concrete type, as the sibling bomb test does."""
    with pytest.raises(EntitiesForbidden) as ei:
        fromstring(XXE_NETWORK)
    assert isinstance(ei.value, ValueError)  # lands in fo's except


def test_fo_2_default_path_does_not_crash_on_deep_input():
    """``fromstring`` itself never ``RecursionError``s on deep input: CPython's expat
    parses iteratively in C, so even a very deep document parses (it does not hang or
    take the process down). This is the default-path never-crash guarantee. (We do NOT
    serialize the result — that recursive op is the documented ``RecursionError``; see
    LIMITATIONS.md.)"""
    depth = 50_000
    root = fromstring("<a>" * depth + "</a>" * depth)
    assert root is not None


def test_fo_2_recommended_limits_bounds_depth_typed():
    """``limits=RECOMMENDED_LIMITS`` rejects an over-deep document at the parse boundary
    with a typed ``DepthExceeded`` that is a ``ValueError`` (lands in fo's ``except``),
    before a deep tree a downstream recursive op could choke on is ever built."""
    over = RECOMMENDED_LIMITS.max_depth + 500
    with pytest.raises(DepthExceeded) as ei:
        fromstring("<a>" * over + "</a>" * over, limits=RECOMMENDED_LIMITS)
    assert isinstance(ei.value, (LimitExceeded, ValueError))


def test_fo_2_recommended_limits_bounds_attributes_typed():
    """``limits=RECOMMENDED_LIMITS`` rejects an attribute flood with a typed
    ``AttributesExceeded`` (a ``ValueError``)."""
    n = RECOMMENDED_LIMITS.max_attributes + 50
    attrs = " ".join(f'a{i}="{i}"' for i in range(n))
    with pytest.raises(AttributesExceeded) as ei:
        fromstring(f"<e {attrs}/>", limits=RECOMMENDED_LIMITS)
    assert isinstance(ei.value, (LimitExceeded, ValueError))


# ---- bounded-TIME evidence (improvement 2): never-HANG, measured not asserted ----
# A never-HANG tripwire, NOT a perf gate: observed times for these inputs are well under
# ~0.2 s, so this ~50-100x ceiling fires only on a genuine hang (infinite/minutes), never
# on CI jitter. The point is termination, not a latency number.
_HANG_CEILING_S = 10.0

_PATHOLOGICAL = {
    "deep_nesting": "<a>" * 50_000 + "</a>" * 50_000,
    "attribute_flood": "<e " + " ".join(f'a{i}="{i}"' for i in range(100_000)) + "/>",
    "wide_fanout": "<r>" + "<c/>" * 100_000 + "</r>",
}


@pytest.mark.parametrize("label", list(_PATHOLOGICAL))
def test_fo_2_bounded_time_default(label):
    """Pathological-but-legal structural input TERMINATES fast on the DEFAULT path
    (expat + TreeBuilder is linear in input; no regex/backtracking surface = no ReDoS).
    A raise counts as termination — we are proving it never hangs, not that it parses."""
    xml = _PATHOLOGICAL[label]
    start = time.perf_counter()
    try:
        fromstring(xml)
    except ValueError:
        pass  # a typed refusal is still termination
    assert time.perf_counter() - start < _HANG_CEILING_S


@pytest.mark.parametrize("label", list(_PATHOLOGICAL))
def test_fo_2_bounded_time_capped(label):
    """With ``RECOMMENDED_LIMITS`` the structural inputs FAIL FAST (rejected early), and
    the billion-laughs bomb is refused at declaration — never a hang."""
    xml = _PATHOLOGICAL[label]
    start = time.perf_counter()
    try:
        fromstring(xml, limits=RECOMMENDED_LIMITS)
    except ValueError:
        pass
    assert time.perf_counter() - start < _HANG_CEILING_S


def test_fo_2_billion_laughs_bounded_time():
    """The entity bomb is refused at the declaration in negligible time — it is never
    expanded, so it cannot hang."""
    start = time.perf_counter()
    with pytest.raises(EntitiesForbidden):
        fromstring(BILLION_LAUGHS)
    assert time.perf_counter() - start < _HANG_CEILING_S


# ---------------------------------------------------------------------------
# Point 3 — the defusedxml.common exception types survive s/defusedxml/purexml/.
# ---------------------------------------------------------------------------
def test_fo_3_defusedxml_exception_catches_refusal():
    """``from purexml.common import DefusedXmlException`` then ``except DefusedXmlException``
    catches a purexml refusal — fo's existing handlers transfer with zero logic change."""
    from purexml.common import DefusedXmlException

    try:
        fromstring(BILLION_LAUGHS)
    except DefusedXmlException:
        pass  # caught — the migration holds
    else:
        pytest.fail("expected a refusal caught by DefusedXmlException")


def test_fo_3_common_surface_are_valueerror_subclasses():
    """The names fo catches all live in ``purexml.common`` and are ``ValueError``
    subclasses at the same MRO position as defusedxml's, so ``except ValueError`` and the
    named excepts both transfer."""
    from purexml.common import (
        DefusedXmlException,
        EntitiesForbidden as CommonEntitiesForbidden,
        ExternalReferenceForbidden as CommonExternalReferenceForbidden,
    )

    for exc in (DefusedXmlException, CommonEntitiesForbidden,
                CommonExternalReferenceForbidden):
        assert issubclass(exc, ValueError)


# ---------------------------------------------------------------------------
# Point 4 — determinism (fo's Pillar 1: identical input → identical output).
# ---------------------------------------------------------------------------
def test_fo_4_repeated_parse_identical():
    """Identical input → identical tree across many parses (no run-to-run drift)."""
    xml = '<r><a z="1" a="2" m="3">x</a><a>y</a></r>'
    first = _c14n(fromstring(xml))
    assert all(_c14n(fromstring(xml)) == first for _ in range(25))


def test_fo_4_attribute_order_is_document_order():
    """No dict/set-order leakage in the tree fo receives — attribute order is the
    document order, deterministically."""
    root = fromstring('<e c="3" a="1" b="2" d="4"/>')
    assert list(root.keys()) == ["c", "a", "b", "d"]


# ---------------------------------------------------------------------------
# Point 5 — fo's exact flat read surface + the 3.10 floor.
# ---------------------------------------------------------------------------
def test_fo_5_flat_consumer_surface():
    """fo's exact read surface: ``.tag`` (Clark-notation), ``.iter(tag)``, ``.get``,
    ``.text``, and direct child iteration — all iterative, safe at any depth."""
    xml = ("<wb xmlns='urn:s'><sheets>"
           "<sheet name='S1'>  hi  </sheet><sheet name='S2'/>"
           "</sheets></wb>")
    root = fromstring(xml)
    assert root.tag == "{urn:s}wb"                                  # .tag (Clark)
    sheets = list(root.iter("{urn:s}sheet"))                        # .iter(Clark-tag)
    assert [s.get("name") for s in sheets] == ["S1", "S2"]          # .get
    assert sheets[0].text.strip() == "hi"                           # .text
    assert {c.tag for c in root} == {"{urn:s}sheets"}               # child iteration


def test_fo_5_python_floor_stays_3_10():
    """'Never bind a consumer's floor' — fo's install floor is 3.10 (chardet-imposed). A
    silent bump past 3.10 would re-block fo on a runtime it still supports, so guard the
    DECLARED floor: a bump must be a conscious decision, and it fails CI here, not at fo.
    (Substring check, not ``tomllib`` — tomllib is 3.11+, and this test must run on 3.10.)"""
    text = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    # ``[^"]*`` on both sides tolerates a future upper bound (e.g. ``">=3.10,<4.0"``)
    # without weakening the guard — a bump to ``>=3.11`` still has no ``>=3.10`` and fails.
    assert re.search(r'requires-python\s*=\s*"[^"]*>=\s*3\.10[^"]*"', text), (
        "the 3.10 floor is fo's adoption requirement — re-open with Russell before bumping"
    )


# ---------------------------------------------------------------------------
# Point 6 — purexml.__version__ is a plain, checksum-stable str.
# ---------------------------------------------------------------------------
def test_fo_6_version_is_plain_str():
    """fo stamps ``purexml.__version__`` into ScanContext.dependencies + a manifest
    checksum — it must stay a plain, sane version ``str`` (a non-string/odd-repr broke
    fo's determinism before)."""
    v = purexml.__version__
    assert isinstance(v, str) and v, "purexml.__version__ must be a non-empty str"
    assert re.match(r"^\d+\.\d+", v), f"unexpected version repr: {v!r}"
