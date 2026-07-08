<!-- Plain markdown image with an ABSOLUTE raw URL (not <picture>/<img>): the GitHub iOS
     app doesn't render <picture>, and PyPI doesn't resolve relative paths — markdown ![]
     with a raw.githubusercontent URL renders on all three (GitHub web + mobile, PyPI). -->
![purexml logo](https://raw.githubusercontent.com/russalo/purexml/main/assets/logo-light.svg)

# purexml

> Safely parse untrusted XML using only the Python standard library.

[![PyPI](https://img.shields.io/pypi/v/purexml)](https://pypi.org/project/purexml/)
[![tests](https://img.shields.io/github/actions/workflow/status/russalo/purexml/tests.yml?branch=main&label=tests)](https://github.com/russalo/purexml/actions/workflows/tests.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/purexml)](https://pypi.org/project/purexml/)
![runtime deps: zero](https://img.shields.io/badge/runtime%20deps-zero-brightgreen)
![pure stdlib](https://img.shields.io/badge/pure-stdlib-blue)
![coverage ≥90%](https://img.shields.io/badge/coverage-%E2%89%A590%25-brightgreen)
![lint: ruff](https://img.shields.io/badge/lint-ruff-30173D)
![types: mypy](https://img.shields.io/badge/types-mypy-blue)
![differentially fuzzed](https://img.shields.io/badge/differentially-fuzzed-blueviolet)
![License: MIT](https://img.shields.io/badge/license-MIT-blue)

**purexml is a zero-dependency, drop-in replacement for [`defusedxml`](https://pypi.org/project/defusedxml/).**
It hardens Python's standard-library XML parsers against the known attack classes —
entity-expansion bombs, external-entity resolution (XXE), and external-DTD retrieval —
and hands back the same standard `xml.etree` / `minidom` / SAX objects your code already
expects. Migrating is a literal find-and-replace: `s/defusedxml/purexml/`.

![How purexml defends untrusted XML in two layers: purexml's own Python-layer handlers block entity bombs, XXE and external-DTD resolution version-independently, while the libexpat parser layer mitigates parser-level DoS depending on your runtime; the result is a standard, trusted xml.etree tree.](https://raw.githubusercontent.com/russalo/purexml/main/assets/defense-layers.svg)

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

```sh
pip install purexml
```

Then the only change to your code is the import path:

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

**v1.0.0 — the public contract is frozen and binding.** The `defusedxml`-mirror surface
won't move under you without a 2.0 (see [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md)).

- Runs on **CPython 3.10–3.13**, zero runtime dependencies.
- Correctness is **oracle-gated against `defusedxml` every release** — C14N + event-stream
  equivalence over a real corpus, an adversarial attack battery, and differential fuzzing
  (see [`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md)).
- The contract freeze was ratified with the anchor consumer (file-observer) — see
  [`docs/v1.0.0_RFC_Specification.md`](docs/v1.0.0_RFC_Specification.md). The opt-in
  defense-in-depth (`Limits`, `security_report()`) stays **provisional** (it tracks the
  moving libexpat threat landscape).
- **On PyPI:** `pip install purexml` — zero runtime dependencies.
- **License: MIT.**

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
source, maximum reuse.

---

*Built by [**russalo**](https://blog.russalo.com) — more at [blog.russalo.com](https://blog.russalo.com).*
