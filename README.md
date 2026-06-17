# purexml

> Safely parse untrusted XML using only the Python standard library.

purexml is a pure-Python, zero-runtime-dependency replacement for `defusedxml`:
it returns the same parse results the stdlib parser would (standard `xml.etree`
objects) while blocking the known XML attack classes — entity-expansion bombs,
external-entity resolution (XXE), and external DTD retrieval — exactly as
`defusedxml` does. As of v0.3 it mirrors **`defusedxml.ElementTree`'s full
surface** (`fromstring`, `parse`, `iterparse`, `fromstringlist`, `XML`,
`XMLParser`, `tostring`, the `forbid_*` knobs), so migrating off `defusedxml` is a
literal `s/defusedxml/purexml/`. It is a security control, not a format reader;
correctness is validated oracle-gated against `defusedxml`.

## Status

**Working — current v0.3.1 (2026-06-16); complete `defusedxml.ElementTree`
drop-in** (the family completed at v0.3.0; v0.3.1 is Tier-1 hardening — a
structural no-I/O guard). All ElementTree parse entry points are implemented,
stdlib-only, and
validated against `defusedxml` as an oracle (C14N same-parse + event-stream
equivalence over a real corpus, an adversarial attack battery, and a 3.10–3.13 CI
matrix). Runs on CPython ≥3.10. No public contract is frozen yet (binds at v1.0),
and it is **not published**: the vendor-vs-first-party adoption model (and with it
PyPI/name/license) is deferred to v1.0 — see *License*. Path to 1.0:
[`docs/ROADMAP-to-1.0.md`](docs/ROADMAP-to-1.0.md). Latest spec + audit:
[`docs/v0.3.0_RFC_Specification.md`](docs/v0.3.0_RFC_Specification.md),
[`docs/COMPLIANCE-v0.3.md`](docs/COMPLIANCE-v0.3.md); north star:
[`docs/FO_REQUIRED_COMPATIBILITY.md`](docs/FO_REQUIRED_COMPATIBILITY.md).

## Stack

See [`STACK.md`](STACK.md) for the language (Python ≥3.10), runtime, dependencies
(zero at runtime), and CI. All stack-specific commands live there.

## Quickstart

```bash
pip install -e ".[dev]"   # editable install + pytest (the defusedxml oracle is dev-only)
python -m pytest tests/ -q
```

No CLI — it's a library. The canonical namespace mirrors `defusedxml.ElementTree`,
so adoption is a literal `s/defusedxml/purexml/`:

```python
from purexml.ElementTree import fromstring, parse, iterparse   # was: defusedxml.ElementTree
root = fromstring(untrusted_xml_text)        # raises on bomb / XXE / external DTD / malformed
tree = parse("untrusted.xml")                # hardened ElementTree
for event, elem in iterparse("big.xml"):     # hardened streaming
    ...
```

`from purexml import fromstring` also works (top-level convenience re-export).

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — agent instructions for working in this repo
- [`HISTORY.md`](HISTORY.md) — running index of all versions, specs, and compliance reports
- [`CONVENTIONS.md`](CONVENTIONS.md) — naming, version-bump rules, document promotion paths
- [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md) — consumer-facing stability commitments *(delete if no stable public surface)*
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
