# Compatibility with defusedxml

purexml is a drop-in for the **`defusedxml.ElementTree` family**: migration is
`s/defusedxml/purexml/`. This document is the honest detail behind "drop-in" — what
matches exactly, the few edges, and the evidence.

## The contract

For the ElementTree family, purexml matches `defusedxml` on:

- **API** — same call names and signatures: `fromstring`, `parse`, `iterparse`,
  `fromstringlist`, `XML`, `XMLParser`, `tostring`, `ParseError`.
- **Defaults** — `forbid_dtd=False`, `forbid_entities=True`, `forbid_external=True`,
  and the same `forbid_*` parameters (names, order, defaults).
- **Parse results** — **C14N-equivalent, or both raise**, verified per release against
  the `defusedxml` oracle over a real-document corpus *and* a seeded differential fuzzer:
  **0 disagreements** (see [`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md)). "C14N-equivalent"
  means the canonical XML is identical — the precise, tested claim (not a looser
  "byte-identical" hand-wave).

## Exceptions — one thing to know

Both libraries raise the **same-named** exceptions, and **both subclass `ValueError`**:

| condition | defusedxml raises | purexml raises | both are |
|---|---|---|---|
| entity bomb / declaration | `defusedxml…EntitiesForbidden` | `purexml…EntitiesForbidden` | `ValueError` |
| external entity/DTD fetch | `…ExternalReferenceForbidden` | `…ExternalReferenceForbidden` | `ValueError` |
| DTD when `forbid_dtd=True` | `…DTDForbidden` | `…DTDForbidden` | `ValueError` |
| malformed input | `xml.etree.ElementTree.ParseError` | `xml.etree.ElementTree.ParseError` | (identical) |

So these keep working unchanged after the swap:
- `except ValueError:` — **equivalent** (both hierarchies subclass it).
- `except EntitiesForbidden:` (etc.) — **equivalent**, because the `s/defusedxml/purexml/`
  swap moves the import too (`purexml.EntitiesForbidden`).

**The one edge:** if you catch defusedxml's **base class by name** —
`except defusedxml.common.DefusedXmlException:` — purexml's exceptions are **not** that
class (they share the same `ValueError` ancestry, not the `DefusedXmlException` base).
Catch [`purexml.PureXMLError`](src/purexml/errors.py) instead, or narrow to `ValueError`.
This is the only catch-clause that needs a change beyond the import swap.

## Deliberate behavioral edges (matching the oracle exactly)

"Equivalent" means matching defusedxml's **allow** behavior as much as its **block**
behavior — purexml does not over-block:

- An **unresolved external-DTD declaration parses** (no fetch is attempted) — only
  *attempted resolution* is blocked. Over-blocking it would break equivalence.
- An **entity-free DOCTYPE / internal subset** is allowed (it's `forbid_dtd=False` by
  default, same as defusedxml).

The **one sanctioned divergence** is opt-in and default-off: passing `Limits` makes
purexml reject pathological-but-legal structural input (deep nesting / attribute floods /
giant documents) that defusedxml would accept. With the default `limits=None`, purexml
stays byte-for-byte the defusedxml mirror. See [`LIMITATIONS.md`](LIMITATIONS.md).

## Scope — what's covered

| defusedxml module | purexml | notes |
|---|---|---|
| `defusedxml.ElementTree` | ✅ full family | the surface most projects use |
| `defusedxml` top-level (`fromstring`, …) | ✅ | re-exported at `purexml` top level |
| `defusedxml.minidom` / `.sax` / `.pulldom` | ⬜ not yet | open an issue if you need them |
| `defusedxml.expatreader` / `.expatbuilder` | ⬜ not yet | — |
| `defusedxml.xmlrpc` / deprecated `.lxml` | ⬜ not planned | — |

purexml is a hardened **reader**, not a writer or a validator, and assumes CPython's
`pyexpat` (the standard runtime).

## Beyond defusedxml (additive — never changes the default)

purexml adds, all **opt-in / read-only** so the drop-in promise is never violated:
`security_report()` (runtime posture), `python -m purexml` (the same as a CLI),
`Limits` (structural-DoS caps), the libexpat version-awareness API. None of these alter
default parse behavior.
