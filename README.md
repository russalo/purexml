# purexml

> Safely parse untrusted XML using only the Python standard library.

purexml is a pure-Python, zero-runtime-dependency replacement for `defusedxml`:
it returns the same parse result the stdlib parser would (an
`xml.etree.ElementTree.Element`) while blocking the known XML attack classes —
entity-expansion bombs, external-entity resolution (XXE), and external DTD
retrieval — exactly as `defusedxml` does. The whole consumer surface is one
hardened call, `fromstring(text) -> Element`. It is a security control, not a
format reader; correctness is validated oracle-gated against `defusedxml`.

## Status

**Early development — v0.1.0 RFC approved (2026-06-16); implementation pending.**
No public contract is frozen. Design lives in the approved RFC
(`docs/v0.1.0_RFC_Specification.md`) and the capability north star
(`docs/TARGET_SPECIFICATION.md`); implementation has not landed. Not published —
see *License* on the open adoption model.

## Stack

See [`STACK.md`](STACK.md) for the language, runtime, dependencies, and any
language-variant adaptations of this template (Python `pyproject.toml` /
Go `justfile`, etc.). All stack-specific commands live there.

## Quickstart

```bash
pip install -e ".[dev]"   # editable install + pytest (the defusedxml oracle is dev-only)
python -m pytest tests/ -q
```

There is no CLI. Intended use is a single library call (once v0.1.0 lands):

```python
from purexml import fromstring
element = fromstring(untrusted_xml_text)   # raises on bomb / XXE / external DTD / malformed
```

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — agent instructions for working in this repo
- [`HISTORY.md`](HISTORY.md) — running index of all versions, specs, and compliance reports
- [`CONVENTIONS.md`](CONVENTIONS.md) — naming, version-bump rules, document promotion paths
- [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md) — consumer-facing stability commitments *(delete if no stable public surface)*
- [`LIMITATIONS.md`](LIMITATIONS.md) — what this project deliberately does **not** do
- [`SECURITY.md`](SECURITY.md) — security policy, scope, and how to report vulnerabilities
- `docs/` — RFCs, compliance reports, and standards-tracking notes per release

## License

**Undecided — tracked, not yet chosen.** The license is tied to the open
**adoption model** (vendor into file-observer vs. ship as a first-party
dependency — see `scratch/packaging_and_naming_notes.md`), which is not yet
decided. The russalo default for a distributable library is AGPL-3.0 + dual
commercial; a vendored unit would inherit the host project's terms instead. To
be set with Russell when the adoption model is chosen — do not publish before
then.
