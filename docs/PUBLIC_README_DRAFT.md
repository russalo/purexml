<!-- PUBLIC README — tracked CANDIDATE for the publish debut (under review).
     SWAPS IN as the repo-root README.md at publish; the live README.md keeps
     dev/internal context until then. Audience: a security engineer landing cold,
     deciding whether to drop defusedxml. Frame: maintained successor (approved 2026-06-17).
     [[STRATEGIC]] markers = Russell's positioning/naming/license calls, left open. -->

# purexml

> Safely parse untrusted XML with **zero third-party dependencies** — the
> maintained, standard-library-only successor to `defusedxml`.

![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![runtime deps: zero](https://img.shields.io/badge/runtime%20deps-zero-brightgreen)
![pure standard library](https://img.shields.io/badge/pure-stdlib-blue)
<!-- Honest now (all true today): the Python matrix is CI-grounded; zero runtime deps +
     stdlib-only are hard, structurally-guarded contracts. Static badges, render anywhere.
     Activates when the repo goes public:
       ![tests](https://img.shields.io/github/actions/workflow/status/russalo/purexml/tests.yml?label=tests)
     Added at publish, once decided (NOT honest yet — omitted on purpose):
       PyPI version (not published) · license (undecided) · downloads (not published).
     [[STRATEGIC: final tagline/positioning + the publish-time badges are Russell's call.]] -->

`defusedxml` is the library [OWASP's XXE cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
and Python's own docs point you to for parsing untrusted XML. Its last stable
release was **0.7.1 in March 2021**; the 0.8.0 successor never shipped (stalled at
`rc2`). Meanwhile the layer its protection rides on kept moving — libexpat shipped
multiple DoS fixes through 2024–2026 (CVE-2023-52425, and the 2.7.4 → 2.8.1 train)
that a frozen package neither tracks nor tells you about.

**purexml is the same protection, maintained — and only the standard library.**
It returns ordinary `xml.etree` objects while blocking the known XML attack classes
(entity-expansion bombs, XXE, external-DTD/entity resolution), behaviorally
*identical to `defusedxml` at its defaults* — proven, not asserted (see *Trust*).

## Why purexml

- **Drop-in.** Migrating off `defusedxml` is a literal `s/defusedxml/purexml/`:
  ```python
  from purexml.ElementTree import fromstring, parse, iterparse   # was: defusedxml.ElementTree
  ```
  Same calls, same defaults, same exceptions, byte-identical parse results.
- **Zero runtime dependencies.** Pure standard library (`xml.parsers.expat` +
  `xml.etree`). Nothing third-party enters your import path — and a CI-gated test
  *proves* `purexml` imports no network/filesystem/subprocess module, so it
  **cannot fetch or shell out, by construction.**
- **Maintained — it tracks the moving target.** purexml knows your runtime's
  libexpat version and tells you what it actually protects you against *today*
  (`security_report()`), and folds new XML-attack research into its corpus. The
  thing `defusedxml` stopped being in 2021.
- **Stronger when you ask, never by surprise.** Opt-in, default-off
  defense-in-depth `defusedxml` never offered — structural-DoS caps (`Limits`),
  the OWASP `forbid_dtd=True` strict mode — so the drop-in promise is never violated.

## Install

[[STRATEGIC: final package name + PyPI availability are Russell's call.]]
```sh
pip install purexml
```

## Quickstart

```python
from purexml.ElementTree import fromstring, parse

root = fromstring(untrusted_xml)      # raises on bomb / XXE / external DTD / malformed
tree = parse("untrusted.xml")         # hardened ElementTree
```
`from purexml import fromstring` also works (top-level convenience).

### Know your runtime's posture (the part `defusedxml` can't do)

```python
import purexml
print(purexml.security_report())
```
```
purexml security posture
  libexpat version: 2.8.1
    meets safe floor (2.6.0): yes
    meets recommended (2.8.1): yes
  mitigations (where each attack class is handled on this runtime):
    attribute_collision_dos_cve_2026_45186 : mitigated-by-libexpat
    billion_laughs                         : blocked-by-purexml
    content_token_overflow_cve_2026_25210  : mitigated-by-libexpat
    external_dtd_retrieval                 : blocked-by-purexml
    external_entity_xxe                    : blocked-by-purexml
    large_tokens_cve_2023_52425            : mitigated-by-libexpat
    quadratic_blowup                       : blocked-by-purexml
    structural_dos_depth_attrs_size        : opt-in (pass Limits)
```
One call tells you which attack classes are blocked by purexml, which ride on your
libexpat version (and whether yours is current), and what you can opt into.

### Opt-in hardening (default-off)

```python
from purexml import fromstring, RECOMMENDED_LIMITS
root = fromstring(untrusted_xml, limits=RECOMMENDED_LIMITS)   # bound deep nesting / attr floods / giant docs
```

## Trust — proven, not promised

A security control is only as good as its evidence. purexml's is the headline:

- **Continuously proven equivalent.** Every release is C14N + event-stream diffed
  against `defusedxml` over a real corpus and a seeded differential fuzzer —
  **0 disagreements** across hundreds of real documents and ~1000s of generated
  ones. "Drop-in" is a tested fact per release, not a claim.
- **Cannot reach the network or filesystem — structurally.** A CI test asserts the
  package imports only the stdlib `xml` (+ pure data modules); no `socket`,
  `urllib`, `subprocess`, `os`, …
- **Tested on every Python it claims** (3.10–3.13) on every push.
- **Honest about its edges** — see *Scope* and `LIMITATIONS`.

## Scope

purexml mirrors the **`defusedxml.ElementTree` family** — the part the large
majority of projects actually use: `fromstring`, `parse`, `iterparse`,
`fromstringlist`, `XML`, `XMLParser`, `tostring`, `ParseError`, the `forbid_*`
knobs. `minidom` / `sax` / `pulldom` are not yet covered — open an issue if you
need them.

It is a hardened **reader**, not a writer or a validator. It assumes CPython's
`pyexpat` (the standard runtime).

## Requirements

CPython ≥ 3.10. No runtime dependencies.

## Security

Found a parse that should have been blocked, an unexpected fetch, or a divergence
from `defusedxml`? See [`SECURITY.md`](SECURITY.md). [[STRATEGIC: public disclosure channel.]]

## License

[[STRATEGIC: Russell's call, set at publish.]]
