# Migrating from `defusedxml` to purexml

purexml is a **behavioral mirror of `defusedxml`** built on the Python standard
library alone. For the **default drop-in path**, migration is a literal find-and-replace
of the import path — `s/defusedxml/purexml/`: the same parses succeed, the same attacks
are blocked, the same exception types are raised, and you get back the same standard
stdlib objects (`xml.etree` `Element`, `xml.dom.minidom.Document`, SAX events). A few
**deliberate differences** — all noted in the per-module sections below — apply only if
you rely on them: `minidom(parser=...)` is refused rather than silently patched (stricter),
and purexml adds opt-in structural-DoS caps that are **off by default**. The reason
purexml can mirror `defusedxml` at all: it is not an open-ended parser, it is a *closed
set of hardening behaviors* layered on the stdlib parser — purexml delivers those same
behaviors on the stdlib directly.

> **Why migrate.** One fewer third-party dependency (purexml has **zero** runtime
> deps), and a *maintained* implementation of the same security model — `defusedxml`
> has been frozen since 2021, while purexml tracks the moving CPython/libexpat threat
> landscape (see [`ROADMAP-to-1.0.md`](ROADMAP-to-1.0.md) and `security_report()`).

For runnable versions of everything below, see [`../examples/`](../examples/).

---

## The core rule

```diff
- from defusedxml.ElementTree import fromstring, parse, iterparse
+ from purexml.ElementTree  import fromstring, parse, iterparse
```

Defaults are identical to defusedxml: `forbid_dtd=False`, `forbid_entities=True`,
`forbid_external=True`. Call sites do not change.

## Coverage at a glance

| defusedxml module | purexml | Status |
|---|---|---|
| `defusedxml.ElementTree` | `purexml.ElementTree` | ✅ full family (`fromstring`, `parse`, `iterparse`, `fromstringlist`, `XML`, `XMLParser`, `tostring`, `forbid_*`) |
| `defusedxml.minidom` | `purexml.minidom` | ✅ `parse`, `parseString` |
| `defusedxml.sax` | `purexml.sax` | ✅ `make_parser`, `parse`, `parseString` |
| `defusedxml.expatreader` | `purexml.expatreader` | ✅ the SAX reader engine |
| `defusedxml.xmlrpc` | `purexml.xmlrpc` | ✅ `monkey_patch` / `unmonkey_patch` |
| `defusedxml.common` | `purexml.common` | ✅ exception catch-site aliases |
| `defusedxml.pulldom` | — | Deferred (measured-negligible usage) — [open an issue](../CONTRIBUTING.md) if you need it |
| `defusedxml.lxml` | — | **Excluded by design** — it wraps the third-party `lxml`, which would break purexml's zero-dependency, stdlib-only contract (and it is deprecated upstream) |

---

## Per-module migration

### `ElementTree`

```diff
- from defusedxml.ElementTree import fromstring, parse, iterparse, XML, XMLParser, tostring
+ from purexml.ElementTree  import fromstring, parse, iterparse, XML, XMLParser, tostring
```

`fromstring(text)` returns a standard `xml.etree.ElementTree.Element` — your existing
`.iter()` / `.find()` / `.get()` / `.text` code is unchanged. `fromstring` accepts
**both `str` and `bytes`** (pass bytes when the document carries an encoding
declaration, so the parser reads it). `parse`/`iterparse` work on files exactly as the
stdlib versions do, hardened.

> **`fromstringlist` is a purexml addition, not a rename.** `defusedxml.ElementTree`
> does *not* wrap `fromstringlist`, but the stdlib has it — so purexml hardens it too.
> If you parse untrusted chunks with `xml.etree.ElementTree.fromstringlist`, switch
> those calls to `purexml.ElementTree.fromstringlist` (there is no `defusedxml`
> equivalent to migrate *from*).

### `minidom`

```diff
- from defusedxml.minidom import parseString, parse
+ from purexml.minidom  import parseString, parse
```

Returns a standard `xml.dom.minidom.Document`. **One deliberate difference:** passing
your own `parser=` raises `NotSupportedError` (a foreign parser would bypass the
hardening) rather than silently patching it — purexml is *stricter* here. If you were
relying on `parser=`, drop it; the default hardened builder is what you want.

### `sax`

```diff
- from defusedxml.sax import make_parser, parse, parseString
+ from purexml.sax  import make_parser, parse, parseString
```

Drives your own `ContentHandler`. **`parseString` is bytes-only** — this mirrors
defusedxml exactly (both raise `TypeError` on a `str`). Malformed input raises the
stdlib `xml.sax.SAXParseException` (not a purexml exception), unchanged.

### `xmlrpc`

```diff
- from defusedxml.xmlrpc import monkey_patch, unmonkey_patch
+ from purexml.xmlrpc  import monkey_patch, unmonkey_patch
```

This one is a **monkeypatch**, not a parse function (same shape as
`defusedxml.xmlrpc`): `monkey_patch()` installs a defused expat parser plus a bounded
gzip decode (`MAX_DATA`, an anti-decompression-bomb cap) onto `xmlrpc.client`/`server`;
`unmonkey_patch()` restores the originals. All `xmlrpc`/`gzip` imports are lazy, so
`import purexml` never pulls the network-capable transport.

### `common` (exception catch sites)

```diff
- from defusedxml.common import DefusedXmlException
+ from purexml.common  import DefusedXmlException
```

`purexml.common` re-exports the block exceptions and aliases
`DefusedXmlException = PureXMLError`, so a catch-all like `except DefusedXmlException`
migrates verbatim across every module.

---

## Exception mapping

purexml's block exceptions keep defusedxml's **names** and its `ValueError` MRO
position, so both `except ValueError` and the named excepts transfer unchanged.

| Condition | Exception | Base |
|---|---|---|
| Entity declaration (billion-laughs / quadratic / declared XXE) | `EntitiesForbidden` | `PureXMLError` → `ValueError` |
| External reference resolution attempted | `ExternalReferenceForbidden` | `PureXMLError` → `ValueError` |
| DOCTYPE seen while `forbid_dtd=True` | `DTDForbidden` | `PureXMLError` → `ValueError` |
| Unsupported operation (e.g. minidom `parser=`) | `NotSupportedError` | `PureXMLError` → `ValueError` |
| **Opt-in** structural cap exceeded (see below) | `LimitExceeded` (`DepthExceeded` / `AttributesExceeded` / `SizeExceeded`) | `PureXMLError` → `ValueError` |
| **Malformed** XML | `xml.etree.ElementTree.ParseError` (or `SAXParseException` for sax) | *stdlib — unchanged* |

`purexml.common.DefusedXmlException` is an alias for `PureXMLError` (the base of all
the refusals above except the stdlib malformed error), so it catches any purexml
refusal exactly as it caught a defusedxml one.

> **One precise caveat.** `fromstring` itself never raises `RecursionError` on deep
> input (CPython's expat parses iteratively). The residual is *downstream*: feeding a
> very deep tree to a recursive op (`ET.tostring`, `copy.deepcopy`) past
> `sys.getrecursionlimit()` raises `RecursionError` — a `RuntimeError`, which escapes
> `except ValueError`. Flat access (`.iter`/`.get`/`.text`) never triggers it; and
> `max_depth` (below) rejects such a document at the parse boundary, before the tree
> exists. See [`../LIMITATIONS.md`](../LIMITATIONS.md).

---

## After you migrate: opt-in extras `defusedxml` never had

These are **off by default**, so adopting purexml changes nothing until you ask for
them. They are additive, not a divergence from the mirror.

**Structural-DoS caps** — bound pathological-but-legal input (deep nesting, attribute
floods, giant documents) that neither defusedxml nor expat's amplification cap covers:

```python
from purexml import fromstring, RECOMMENDED_LIMITS
root = fromstring(untrusted, limits=RECOMMENDED_LIMITS)   # raises LimitExceeded past the caps
```

**Posture visibility** — a read-only report of what each attack class is protected by
on *this* runtime (some parser-level DoS mitigations are libexpat-version-dependent):

```python
import purexml
print(purexml.security_report())        # human-readable; also a frozen value object
# CLI form:  python -m purexml [--json] [--check --min-expat 2.8.2]
```

---

## Checklist

- [ ] Replace `defusedxml` imports with `purexml` (`s/defusedxml/purexml/`).
- [ ] Keep your `except` clauses as they are — the exception types transfer.
- [ ] Drop any `parser=` argument to `minidom.parse`/`parseString` (now `NotSupportedError`).
- [ ] Confirm `sax.parseString` inputs are `bytes` (they had to be under defusedxml too).
- [ ] Remove `defusedxml` from your dependencies. purexml adds none.
- [ ] *(optional)* Pass `limits=RECOMMENDED_LIMITS` where you parse untrusted input.
- [ ] *(optional)* Wire `python -m purexml --check` into CI to pin a libexpat floor.

> **Note on availability.** Until purexml is published to PyPI, depend on it via a git
> or path reference; the import surface above is already stable. Track the publish +
> 1.0 status in [`ROADMAP-to-1.0.md`](ROADMAP-to-1.0.md).
