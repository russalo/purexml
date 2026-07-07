<!-- PUBLIC README — tracked CANDIDATE for the publish debut (under review).
     SWAPS IN as the repo-root README.md at publish; the live README.md keeps
     dev/internal context until then. Audience: a security engineer landing cold,
     deciding whether to drop defusedxml.
     Frame: maintained implementation of the defusedxml security model (rebalanced
     2026-06-17 per external review — evolution of the model, not a reaction to
     defusedxml's status). [[STRATEGIC]] markers = Russell's positioning/naming/
     license/publish-timing calls, left open. -->

<!-- Plain markdown image with an ABSOLUTE raw URL: PyPI doesn't resolve relative paths,
     and neither PyPI nor the GitHub mobile apps render <picture>. Markdown ![] renders on
     all three (GitHub web, GitHub mobile, PyPI); size comes from the SVG width attr. -->
![purexml logo](https://raw.githubusercontent.com/russalo/purexml/main/assets/logo-light.svg)

# purexml

> Safely parse untrusted XML with **zero third-party dependencies** — a maintained,
> standard-library-only implementation of the `defusedxml` security model, with
> runtime posture visibility and optional modern hardening.

<!-- Badges shown now: static shields, every one true TODAY (structural facts + CI-gated
     quality). Honesty discipline — nothing here implies a published or licensed state. -->
![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![runtime deps: zero](https://img.shields.io/badge/runtime%20deps-zero-brightgreen)
![pure standard library](https://img.shields.io/badge/pure-stdlib-blue)
![coverage ≥90%](https://img.shields.io/badge/coverage-%E2%89%A590%25-brightgreen)
![lint: ruff](https://img.shields.io/badge/lint-ruff-30173D)
![types: mypy](https://img.shields.io/badge/types-mypy-blue)
![differentially fuzzed](https://img.shields.io/badge/differentially-fuzzed-blueviolet)

<!-- ── AT PUBLISH: uncomment these DYNAMIC badges (they self-update — they can't silently go
     stale the way a hardcoded shield can) and RETIRE the matching static one above. Each is
     true today; gated only on the public repo + the publish/name decision, not on more work. ──

![CI](https://img.shields.io/github/actions/workflow/status/russalo/purexml/tests.yml?branch=main&label=tests)  (live green/red; needs public repo — replaces nothing)
![PyPI](https://img.shields.io/pypi/v/purexml)                          (needs publish)
![Python versions](https://img.shields.io/pypi/pyversions/purexml)      (dynamic; RETIRE the static Python matrix above)
![Coverage](https://codecov.io/gh/russalo/purexml/branch/main/graph/badge.svg)  (real %; needs Codecov — RETIRE the static coverage badge above)
![License](https://img.shields.io/pypi/l/purexml)                       (license is MIT — badge reads it from PyPI once published)
![OpenSSF Best Practices](https://www.bestpractices.dev/projects/PROJECT_ID/badge)  (enroll at bestpractices.dev → fill PROJECT_ID — the headline credential for a security library)
![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/russalo/purexml/badge)  (optional; supply-chain posture, needs the Scorecard action)

     NOT YET (don't fake): downloads (no traffic yet — low value early); anything implying a
     published/licensed state before those land. Tracker: scratch/publish_prep_checklist.md.
     [[STRATEGIC: package name + which publish-time badges ship are Russell's calls. License = MIT (decided).]] -->

<!-- Hero diagram. SVG renders on both GitHub and the PyPI project page (mermaid does NOT
     render on PyPI). URL is ABSOLUTE (raw.githubusercontent) on purpose: PyPI does not resolve
     relative image paths in the long-description, so a relative path would render on GitHub but
     break on the PyPI page. Resolves once the repo is public on `main`. -->
![How purexml defends untrusted XML in two layers: purexml's own Python-layer handlers block entity bombs, XXE and external-DTD resolution version-independently, while the libexpat parser layer mitigates parser-level DoS depending on your runtime; the result is a standard, trusted xml.etree tree.](https://raw.githubusercontent.com/russalo/purexml/main/assets/defense-layers.svg)

purexml hardens Python's standard-library XML parser against the known untrusted-XML
attack classes — entity-expansion bombs, XXE, external-DTD/entity resolution — and
returns ordinary `xml.etree` objects. Same protections as `defusedxml`, with **zero
third-party dependencies, active maintenance, and a runtime posture report** that tells
you what your interpreter actually protects you against.

## Quickstart

```sh
pip install purexml      # [[STRATEGIC: final package name + PyPI availability — Russell's call]]
```
```python
from purexml.ElementTree import fromstring, parse   # was: defusedxml.ElementTree

root = fromstring(untrusted_xml)      # raises on bomb / XXE / external DTD / malformed
tree = parse("untrusted.xml")         # hardened ElementTree
```
`from purexml import fromstring` also works (top-level convenience).

## Know your runtime's posture

The thing a wrapper around the stdlib usually can't tell you: *what does my interpreter
actually protect me against?* One call, read-only, no parsing:

```python
import purexml
print(purexml.security_report())          # or:  python -m purexml
```
```
purexml security posture            (example on a current runtime)
  libexpat version: 2.8.2
    meets safe floor (2.6.0): yes
    meets recommended (2.8.2): yes
  mitigations (where each attack class is handled on this runtime):
    attribute_collision_dos_cve_2026_45186 : mitigated-by-libexpat
    billion_laughs                         : blocked-by-purexml
    content_token_overflow_cve_2026_25210  : mitigated-by-libexpat
    disproportionate_memory                : mitigated-by-libexpat
    external_dtd_retrieval                 : blocked-by-purexml
    external_entity_xxe                    : blocked-by-purexml
    hash_flooding_cve_2026_41080           : partial-by-libexpat (defense present; upgrade hardens it)
    large_tokens_cve_2023_52425            : mitigated-by-libexpat
    quadratic_blowup                       : blocked-by-purexml
    structural_dos_depth_attrs_size        : opt-in (pass Limits)
```
It separates what **purexml** blocks (at the Python layer, version-independent) from
what your **libexpat** version covers (and whether yours is current) — see *Why not just
rely on modern libexpat?*. `python -m purexml --check` turns it into an opt-in CI gate.

## Why purexml

- **Drop-in.** Migrating off `defusedxml` is `s/defusedxml/purexml/` — same public API,
  same defaults, same exception types; parse behavior matches across our differential
  corpus (see *Trust*).
- **Zero runtime dependencies.** Standard library only (`xml.parsers.expat` +
  `xml.etree`) — nothing third-party in your import path or supply chain.
- **Maintained — it tracks the moving target.** The protection against parser-level DoS
  lives in *libexpat*, which keeps shipping fixes (CVE-2023-52425; the 2.7.4 → 2.8.1 train
  in 2024–2026). purexml knows your runtime's libexpat version, reports what it covers,
  and folds new XML-attack research into its corpus. *(Context: OWASP and the Python docs
  still point to `defusedxml`, whose last stable is 0.7.1 from March 2021 and whose 0.8.0
  stalled at `rc2` — so that tracking isn't happening upstream today. purexml exists to do
  it, and would still earn its place if that changed.)*
- **Stronger when you ask, never by surprise.** Opt-in, default-off defense-in-depth —
  structural-DoS caps (`Limits`), the OWASP `forbid_dtd=True` strict mode — so the
  drop-in promise is never silently violated.

## Migrating from defusedxml

```python
# before
from defusedxml.ElementTree import fromstring, parse, iterparse
# after
from purexml.ElementTree import fromstring, parse, iterparse
```
No code changes for the common `defusedxml.ElementTree` API — same defaults, same
`forbid_*` parameters, same exception hierarchy (`ParseError` for malformed,
`*Forbidden` for blocked, all subclassing `ValueError`). The full contract, the one
catch-clause edge, and what's in/out of scope are in [`COMPATIBILITY.md`](COMPATIBILITY.md);
the compatibility evidence is in *Trust*.

## Trust — evidence, not assertion

A security control is only as good as its evidence:

- **Differentially tested against `defusedxml`, every release.** Each release is diffed
  against the `defusedxml` oracle — **C14N-equivalent, or both raise** — over a
  real-document corpus *and* a seeded differential fuzzer: **0 disagreements** across
  hundreds of real inputs and thousands of generated ones. The compatibility claim is
  measured per release, not asserted. An opt-in [Atheris](https://github.com/google/atheris)
  harness drives coverage-guided fuzzing on demand.
- **No I/O reachable from the parse path — and CI proves it.** purexml imports only the
  standard library's `xml` package (plus pure data structures); a CI-gated test asserts
  it imports **no** network, filesystem, or subprocess module — so it cannot fetch a URL,
  read a file the document points at, or shell out. A structural guarantee, not just a test.
- **Tested on every Python it claims** (3.10–3.13), on every push.
- **Honest about its edges** — see *Scope*, *Threat model*, and [`LIMITATIONS.md`](LIMITATIONS.md).

## Threat model

purexml is for parsing XML from **untrusted sources** — user input, uploads, partner
feeds, APIs, the network. It protects against:

- entity-expansion bombs (billion-laughs, quadratic blowup),
- XXE via external entities (local-file and network),
- external-DTD / external-entity resolution,

raising a catchable exception **before** any expansion, fetch, or file read. It does
**not** provide: XML schema/DTD *validation*, signature/XML-DSig verification,
authorization, or business-rule checks — and it is a hardened **reader**, not a writer.

## Why not just rely on modern libexpat?

Modern libexpat fixes several *parser-level* denial-of-service issues — and purexml
reports which ones your version has. But libexpat does **not** change how the parser
treats entity declarations or external references: blocking billion-laughs, XXE, and
external-DTD/entity resolution is done by purexml's own handlers, at the Python layer,
**independent of the libexpat version** (it refuses the entity declaration before any
expansion). `security_report()` makes the split explicit — `blocked-by-purexml` vs
`mitigated-by-libexpat` — so you can see exactly which layer covers each class.

## Opt-in hardening (default-off)

```python
from purexml import fromstring, RECOMMENDED_LIMITS
root = fromstring(untrusted_xml, limits=RECOMMENDED_LIMITS)   # bound nesting / attr floods / giant docs
```
Default behavior stays a strict mirror of `defusedxml`; you opt into more only by asking.

## Scope

The **`defusedxml.ElementTree` family** — the part the large majority of projects use:
`fromstring`, `parse`, `iterparse`, `XML`, `XMLParser`, `tostring`, `ParseError`, the
`forbid_*` knobs (plus a hardened `fromstringlist` the stdlib has and `defusedxml` doesn't
wrap) — **plus `defusedxml.minidom`** (v0.10), **`defusedxml.sax`**
+ **`.expatreader`** (v0.12), and **`defusedxml.xmlrpc`** (v0.13, `monkey_patch()` — defused
parser + anti-gzip-bomb), and `defusedxml.common` (the `DefusedXmlException` catch alias). The
measured breadth surface is complete; only measured-negligible `pulldom` isn't covered (open an
issue), and the deprecated `lxml` shim is out of scope (it needs the third-party `lxml`, which
would break zero-dependency). Assumes CPython's `pyexpat` (the standard runtime).

## Requirements

CPython ≥ 3.10. No runtime dependencies.

## Security

Report a parse that should have been blocked, an unexpected fetch, or a divergence from
`defusedxml` privately — see [`SECURITY.md`](SECURITY.md). [[STRATEGIC: public disclosure
channel + CVE-handling / supported-versions policy, set at publish.]]

## License

[MIT](LICENSE) — pure open source, zero strings. Drop it into your project and go.
