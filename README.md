# purexml

> Safely parse untrusted XML using only the Python standard library.

![How purexml defends untrusted XML in two layers: purexml's own Python-layer handlers block entity bombs, XXE and external-DTD resolution version-independently, while the libexpat parser layer mitigates parser-level DoS depending on your runtime; the result is a standard, trusted xml.etree tree.](assets/defense-layers.svg)

purexml is a pure-Python, zero-runtime-dependency replacement for `defusedxml`:
it returns the same parse results the stdlib parser would (standard `xml.etree`
objects) while blocking the known XML attack classes — entity-expansion bombs,
external-entity resolution (XXE), and external DTD retrieval — exactly as
`defusedxml` does. It mirrors **`defusedxml.ElementTree`'s full surface**
(`fromstring`, `parse`, `iterparse`, `fromstringlist`, `XML`, `XMLParser`,
`tostring`, the `forbid_*` knobs) and, by measured demand, **`defusedxml.minidom`**
(v0.10), **`defusedxml.sax`** + **`.expatreader`** (v0.12), **`defusedxml.xmlrpc`** (v0.13), and
`defusedxml.common`, so migrating off `defusedxml` is a literal `s/defusedxml/purexml/`. It is a security control, not a format reader;
correctness is validated oracle-gated against `defusedxml`.

Beyond the strict mirror, purexml adds **opt-in, default-off** defense-in-depth
`defusedxml` never had — structural-DoS caps (`Limits`, v0.4; on ElementTree +
minidom + sax as of v0.14) and a read-only
security-posture report (`security_report()`, v0.5) that tells you what your
*runtime* is actually protected against. Both are off by default, so the drop-in
promise is never violated; you get a clean mirror until you ask for more.

## Status

**Working — current v0.14.0 (2026-06-27); complete `defusedxml.ElementTree`
drop-in** (the family completed at v0.3.0) **plus `defusedxml.minidom` + `.common`
(v0.10), `defusedxml.sax` + `.expatreader` (v0.12), and `defusedxml.xmlrpc` (v0.13)** —
the **measured breadth surface is now complete** (only measured-negligible `pulldom`
deferred + third-party `lxml` excluded); next is the 1.0 freeze. Opt-in
mirror-plus along the way: v0.4 structural-DoS caps (`Limits`,
default-off; extended to minidom + sax in v0.14) and the **trust surface** (`security_report()` + shipped audit evidence, v0.5;
posture map extended with the newer expat DoS classes in v0.6 and CVE-2026-41080 in v0.9;
the `python -m purexml` posture CLI in v0.7; a typed public surface + `py.typed` in v0.8).
All ElementTree parse entry points
are implemented, stdlib-only, and validated against `defusedxml` as an oracle (C14N
same-parse + event-stream equivalence over a real corpus, an adversarial attack
battery, seeded differential fuzz, and a 3.10–3.13 CI matrix — see
[`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md), regenerated per release). Runs on
CPython ≥3.10. No public contract is frozen yet (binds at v1.0), and it is **not
published**: the vendor-vs-first-party adoption model (and with it
PyPI/name/license) is deferred to v1.0 — see *License*. Path to 1.0:
[`docs/ROADMAP-to-1.0.md`](docs/ROADMAP-to-1.0.md). Latest spec:
[`docs/v0.14.0_RFC_Specification.md`](docs/v0.14.0_RFC_Specification.md); north star:
[`docs/v1.0_TARGET.md`](docs/v1.0_TARGET.md) and the FO floor at
[`docs/FO_REQUIRED_COMPATIBILITY.md`](docs/FO_REQUIRED_COMPATIBILITY.md).

## Stack

See [`STACK.md`](STACK.md) for the language (Python ≥3.10), runtime, dependencies
(zero at runtime), and CI. All stack-specific commands live there.

## Quickstart

```bash
pip install -e ".[dev]"   # editable install + pytest (the defusedxml oracle is dev-only)
python -m pytest tests/ -q
```

Primarily a library (plus a small posture CLI, below). The canonical namespace
mirrors `defusedxml.ElementTree`, so adoption is a literal `s/defusedxml/purexml/`:

```python
from purexml.ElementTree import fromstring, parse, iterparse   # was: defusedxml.ElementTree
root = fromstring(untrusted_xml_text)        # raises on bomb / XXE / external DTD / malformed
tree = parse("untrusted.xml")                # hardened ElementTree
for event, elem in iterparse("big.xml"):     # hardened streaming
    ...
```

`from purexml import fromstring` also works (top-level convenience re-export).

There's also a posture CLI — `python -m purexml` prints the runtime's XML-security
posture (libexpat version + per-class mitigation map); `--json` for machine-readable
output, `--check [--min-expat X.Y.Z]` as an opt-in CI gate (exit code), `--version`.

### Opt-in defense-in-depth (default-off)

```python
import purexml

# Know your runtime's posture — what each XML attack class is protected by HERE
# (purexml's handlers, the libexpat version, or an opt-in cap). Read-only, no parse.
print(purexml.security_report())          # human-readable; also a frozen value object

# Bound structural DoS (deep nesting / attribute floods / giant docs) — off unless
# you pass Limits; the strict defusedxml mirror is unchanged otherwise.
from purexml import fromstring, RECOMMENDED_LIMITS
root = fromstring(untrusted_xml, limits=RECOMMENDED_LIMITS)   # raises LimitExceeded past the caps
```

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — agent instructions for working in this repo
- [`HISTORY.md`](HISTORY.md) — running index of all versions, specs, and compliance reports
- [`CONVENTIONS.md`](CONVENTIONS.md) — naming, version-bump rules, document promotion paths
- [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md) — consumer-facing stability commitments *(delete if no stable public surface)*
- [`COMPATIBILITY.md`](COMPATIBILITY.md) — drop-in compatibility with `defusedxml` (contract, exception edge, scope)
- [`CHANGELOG.md`](CHANGELOG.md) — public-facing changelog
- [`LIMITATIONS.md`](LIMITATIONS.md) — what this project deliberately does **not** do
- [`SECURITY.md`](SECURITY.md) — security policy, scope, and how to report vulnerabilities
- `docs/` — RFCs, compliance reports, and standards-tracking notes per release

## License

**Deferred to v1.0.** The license rides on the **adoption model** (vendor into
file-observer vs. ship as a first-party dependency — see
`scratch/packaging_and_naming_notes.md`), which is deliberately deferred to v1.0
(decided 2026-06-16). The russalo default for a distributable library is AGPL-3.0
+ dual commercial; a vendored unit would inherit the host project's terms
instead. Until 1.0: package-only in the private repo, no PyPI, no name claim, no
license set.
