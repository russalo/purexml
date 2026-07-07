<!-- Plain markdown image (not <picture>/<img>): the GitHub iOS app's renderer doesn't
     support <picture>, so it showed a broken box. Markdown ![] renders everywhere. -->
![purexml logo](assets/logo-light.svg)

# purexml

> Safely parse untrusted XML using only the Python standard library.

**purexml is a zero-dependency, drop-in replacement for [`defusedxml`](https://pypi.org/project/defusedxml/).**
It hardens Python's standard-library XML parsers against the known attack classes —
entity-expansion bombs, external-entity resolution (XXE), and external-DTD retrieval —
and hands back the same standard `xml.etree` / `minidom` / SAX objects your code already
expects. Migrating is a literal find-and-replace: `s/defusedxml/purexml/`.

![How purexml defends untrusted XML in two layers: purexml's own Python-layer handlers block entity bombs, XXE and external-DTD resolution version-independently, while the libexpat parser layer mitigates parser-level DoS depending on your runtime; the result is a standard, trusted xml.etree tree.](assets/defense-layers.svg)

## Why purexml

- **Zero runtime dependencies.** Pure standard library — drop a third-party dependency
  with no loss of protection (same parses succeed, same attacks blocked).
- **A real drop-in.** Mirrors `defusedxml`'s API and defaults across the surface the
  ecosystem actually imports, validated **oracle-gated against `defusedxml` itself**.
- **Maintained.** `defusedxml` has been frozen since 2021 — the XML threat landscape
  hasn't. purexml tracks the moving libexpat / CPython mitigations and can report what
  your runtime is actually protected against.
- **Opt-in hardening.** Structural-DoS caps and a posture report that `defusedxml`
  lacks — **off by default**, so the drop-in promise is never broken.

## Install & migrate

Until purexml is published to PyPI, depend on it via a git or path reference. Then the
only change to your code is the import path:

```python
# before:  from defusedxml.ElementTree import fromstring
from purexml.ElementTree import fromstring

root = fromstring(untrusted_xml)   # raises on bomb / XXE / external DTD; returns a standard Element
```

Defaults match `defusedxml` exactly (`forbid_entities=True`, `forbid_external=True`,
`forbid_dtd=False`), so nothing else changes.

> Runnable examples for every surface: **[`examples/`](examples/)** ·
> Module-by-module migration guide: **[`docs/MIGRATING.md`](docs/MIGRATING.md)**

## What it covers

Drop-in replacements for the `defusedxml` modules the ecosystem imports:

| purexml module | replaces | surface |
|---|---|---|
| `purexml.ElementTree` | `defusedxml.ElementTree` | `fromstring`, `parse`, `iterparse`, `XML`, `XMLParser`, `tostring`, `forbid_*` |
| `purexml.minidom` | `defusedxml.minidom` | `parse`, `parseString` |
| `purexml.sax` / `.expatreader` | `defusedxml.sax` | `make_parser`, `parse`, `parseString` |
| `purexml.xmlrpc` | `defusedxml.xmlrpc` | `monkey_patch`, `unmonkey_patch` |
| `purexml.common` | `defusedxml.common` | exception catch-site aliases |

`defusedxml.pulldom` is deferred (low measured demand); `defusedxml.lxml` is excluded by
the zero-dependency contract (it wraps the third-party `lxml`).

## Opt-in defense-in-depth

Bounded protections `defusedxml` never had — **default-off**, so the strict mirror is
unchanged until you ask:

```python
import purexml
from purexml import fromstring, RECOMMENDED_LIMITS

# Bound structural DoS (deep nesting / attribute floods / giant documents):
root = fromstring(untrusted, limits=RECOMMENDED_LIMITS)   # raises LimitExceeded past the caps

# See what THIS runtime is actually protected against (read-only; no parse):
print(purexml.security_report())
```

There's also a posture CLI — `python -m purexml` (`--json` for machine output, or
`--check --min-expat X.Y.Z` as an opt-in CI gate).

## Status

**Pre-1.0 — currently v0.14.1.** Working and validated, but the public API is not frozen
yet (it binds at 1.0).

- Runs on **CPython 3.10–3.13**, zero runtime dependencies.
- Correctness is **oracle-gated against `defusedxml` every release** — C14N + event-stream
  equivalence over a real corpus, an adversarial attack battery, and differential fuzzing
  (see [`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md)).
- **Not yet published to PyPI**, and the `purexml` name is not yet claimed — both held for
  a deliberate strategic call.
- **License: MIT.**

The measured drop-in surface is complete; the plan to 1.0 is
[`docs/ROADMAP-to-1.0.md`](docs/ROADMAP-to-1.0.md).

## Documentation

- **[`examples/`](examples/)** — runnable, copy-paste examples for every surface
- **[`docs/MIGRATING.md`](docs/MIGRATING.md)** — the `s/defusedxml/purexml/` migration guide
- [`COMPATIBILITY.md`](COMPATIBILITY.md) — drop-in compatibility contract + exception edge cases
- [`LIMITATIONS.md`](LIMITATIONS.md) — what purexml deliberately does **not** do
- [`SECURITY.md`](SECURITY.md) — security policy and how to report issues
- [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md) — consumer stability commitments (binds at 1.0)
- [`CHANGELOG.md`](CHANGELOG.md) — release notes · [`HISTORY.md`](HISTORY.md) — full per-release record
- [`STACK.md`](STACK.md) — language, runtime, dependencies · [`CONVENTIONS.md`](CONVENTIONS.md) — project conventions

## License

[MIT](LICENSE) — purexml is give-it-away, zero-dependency infrastructure: pure open
source, maximum reuse. Publishing to PyPI and claiming the `purexml` name remain a
separate, deliberate call.
