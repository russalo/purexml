# purexml Public Contract

> **✅ BINDING as of v1.0.0 (2026-07-08; ratified 2026-07-07).** This is the stability commitment from purexml
> to the systems that depend on it. Everything marked **Stable** below will not be removed,
> renamed, or change type or semantics without a **MAJOR** (2.0) version bump. Fields marked
> **Provisional** are explicitly *not* under this contract (§2.2). The frozen surface was
> ratified by Russell and the file-observer steward — see
> [`docs/v1.0.0_RFC_Specification.md`](docs/v1.0.0_RFC_Specification.md); it is guarded
> mechanically by `tests/test_public_contract.py`.
>
> **Not the same as publication.** This contract binds the *codebase* at 1.0.0. Distribution
> (PyPI publication, claiming the `purexml` name) is a separate step; until then, depend on
> purexml via a git or path reference.

---

## 1. What consumers can count on

### 1.1 Version

- **RELEASE_VERSION** — the package version (`purexml.__version__`, a plain `str`; also
  `pyproject.toml`). Consumers may pin it and stamp it into dependency provenance. Semantic
  versioning: **MAJOR** for breaking changes, **MINOR** for additive changes, **PATCH** for
  fixes.
- **SCHEMA_VERSION — n/a.** purexml returns standard stdlib objects
  (`xml.etree.ElementTree.Element`, `xml.dom.minidom.Document`, SAX events), not a versioned
  wire shape, so there is no purexml record schema to version.
- **LOGIC_VERSION** — the hardening mitigation set. Visible for diagnosis (`security_report()`),
  **not** a stability commitment (§3).

### 1.2 Stable top-level surface

The `defusedxml`-mirror surface. Names, signatures, parameter names/order, **defaults**, and
return types below are **Stable** — frozen to 2.0. Migration off `defusedxml` is
`s/defusedxml/purexml/`.

| Namespace / symbol | Signature (defaults are part of the contract) | Stability |
|---|---|---|
| `purexml.ElementTree.fromstring` (also `purexml.fromstring`) | `(text: str\|bytes, forbid_dtd=False, forbid_entities=True, forbid_external=True, *, limits=None) -> Element` | **Stable** |
| `purexml.ElementTree.parse` | `(source, parser=None, forbid_dtd=False, forbid_entities=True, forbid_external=True, *, limits=None) -> ElementTree` | **Stable** |
| `purexml.ElementTree.iterparse` | `(source, events=None, forbid_dtd=False, forbid_entities=True, forbid_external=True, *, limits=None)` | **Stable** |
| `purexml.ElementTree.fromstringlist` | `(sequence, parser=None, forbid_dtd=False, forbid_entities=True, forbid_external=True, *, limits=None) -> Element` | **Stable** |
| `purexml.ElementTree.XMLParser` | `(*, target=None, encoding=None, forbid_dtd=False, forbid_entities=True, forbid_external=True, limits=None)` | **Stable** |
| `purexml.ElementTree.XML` / `XMLParse` / `XMLTreeBuilder` / `tostring` / `ParseError` | aliases + re-exported stdlib | **Stable** |
| `purexml.minidom.parse` / `parseString` | `parseString(string: str\|bytes, parser=None, forbid_*…, *, limits=None) -> Document` | **Stable** |
| `purexml.sax.make_parser` / `parse` / `parseString` | `parseString(string: bytes, handler, …)` — **bytes-only** | **Stable** |
| `purexml.expatreader.create_parser` | `() -> hardened SAX reader` | **Stable** |
| `purexml.xmlrpc.monkey_patch` / `unmonkey_patch` / `defused_gzip_decode` / `MAX_DATA` | monkeypatch shim | **Stable** |
| `purexml.common.DefusedXmlException` (+ block-exception re-exports) | alias of `PureXMLError` | **Stable** |
| `purexml.__version__` | plain `str`, always present | **Stable** |
| `Limits`, `RECOMMENDED_LIMITS`, `security_report`, `SecurityReport`, status constants, the `EXPAT_*` / `assert_expat_secure` surface | opt-in defense-in-depth | **Provisional** (§2.2) |

**Defaults (Stable):** `forbid_entities=True`, `forbid_external=True`, `forbid_dtd=False`.
The default parse path is byte-equivalent to `defusedxml`.

**Runtime floor (Stable):** `requires-python >= 3.10`. purexml will **not raise** its
supported Python floor above 3.10 within the 1.x line (a raise is a 2.0). Lowering the floor
is additive.

### 1.3 Stable exception hierarchy

Frozen and **complete** — every reachable refusal is present. Consumers may catch any level.

```
PureXMLError(ValueError)
├── DTDForbidden
├── EntitiesForbidden
├── ExternalReferenceForbidden
├── NotSupportedError
└── LimitExceeded            [Provisional — opt-in; raised only when limits= is passed]
    ├── DepthExceeded
    ├── AttributesExceeded
    └── SizeExceeded
```

- Every refusal subclasses `ValueError` (mirrors `defusedxml`'s MRO).
- **Malformed** input raises the stdlib `xml.etree.ElementTree.ParseError` (or
  `xml.sax.SAXParseException` for sax) — never a `PureXMLError`.
- `purexml.common.DefusedXmlException` is a **Stable** alias for `PureXMLError`, so
  `except DefusedXmlException` migrates verbatim.

### 1.4 Per-record structure

purexml returns the **stdlib's** objects, so the field structure is the stdlib's, not
purexml's — there is no purexml-specific record schema to pin. `security_report()`'s value
object is **Provisional** (§2.2).

---

## 2. What counts as a breaking change

A change is **breaking** (requires a MAJOR / 2.0 bump) if it, for a **Stable** item:
removes or renames it; changes a signature, parameter name/order, or a **default**; changes
a return type or an exception's identity/MRO position; rejects a previously-valid input
(over-blocking on the default path); or raises the supported Python floor above 3.10.

A change is **additive** (ships in a MINOR) if it adds a new symbol/namespace, a new optional
(keyword) parameter, a new opt-in capability, or lowers the Python floor.

### 2.1 Deprecation policy

A Stable symbol destined for removal in v{N+1}.0 must be marked **deprecated** in at least one
full v{N}.MINOR release before removal, with the deprecation visible in the docs, in
`HISTORY.md`/`CHANGELOG.md`, and (where practical) via a `DeprecationWarning`.

### 2.2 Provisional surface

The opt-in defense-in-depth — `Limits` / `RECOMMENDED_LIMITS`, `security_report()` /
`SecurityReport` + its status vocabulary (`BLOCKED` / `EXPAT_MITIGATED` / `EXPAT_PARTIAL` /
`OPT_IN` / `LIVE`), and the libexpat version-assertion surface — is **Provisional**: it MAY
change in a MINOR release. This is deliberate — these track the *moving* libexpat/CPython
threat landscape, and freezing them would prevent purexml from hardening against new expat
CVE classes without a 2.0 (strictly worse for a security control). The **default drop-in
path never touches them.** Consumers depending on a provisional symbol should pin a specific
MINOR (as file-observer does, recording `RECOMMENDED_LIMITS` + the expat floor in its
dependency provenance) or be ready to adapt.

The provisional → stable promotion criterion is *settled behavior + evidence of value*;
promotions ship in a MINOR and are recorded here + in `HISTORY.md`.

---

## 3. What consumers should NOT count on

Explicitly **not** under the contract:

- **Internal version axes** (LOGIC_VERSION) — visible for diagnosis, bumped freely.
- **Import paths / package layout beyond §1.2** — internal module structure may be
  refactored as long as the §1.2 public surface is preserved.
- **Error message *wording*** — the exception *types* are Stable; the message strings are not.
- **Performance characteristics** — algorithms may change as long as output stays equivalent.
- **Ordering of anything not documented as stable** (attribute order in the returned tree
  *is* stable — it is the document order the stdlib preserves).
- **The Provisional surface** (§2.2).

---

## 4. Backward compatibility policy

Within a MAJOR version, code that works on v{X}.Y continues to work on v{X}.Z (Z > Y) for the
**Stable** surface. Additive (MINOR) changes may introduce new symbols/parameters that older
code simply doesn't use. Tests pinned to v{X}.Y behavior pass on v{X}.Z for Stable items;
Provisional items may require adaptation across MINORs.

---

## 5. Version of this contract

This contract became binding at **v1.0.0 (2026-07-08; ratified 2026-07-07)**. It was ratified by Russell and the
file-observer steward (see [`docs/v1.0.0_RFC_Specification.md`](docs/v1.0.0_RFC_Specification.md))
and is guarded by `tests/test_public_contract.py`. See [`HISTORY.md`](HISTORY.md) for the
1.0.0 entry.
